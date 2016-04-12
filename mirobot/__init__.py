try:
  from queue import Queue
except ImportError:
  from Queue import Queue
from mirobot.socket_handler import SocketHandler
import time
import string
import random
import sys
import json
try:
  import urllib.request as request
except ImportError:
  import urllib2 as request

_sentinel = object()

class Mirobot:
  def __init__(self, address = None, debug = False):
    # Initialisation for the id field
    self.nonce  = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4))
    self.n      = 0
    self.debug = debug

    # callbacks
    self.__on_error    = None
    self.__on_collide  = None
    self.__on_follow   = None

    if address:
      self.connect(address)

  def connect(self, address):
    # Set up the socket handling
    self.__send_q = Queue()
    self.recv_q = Queue()
    self.socket = SocketHandler(address, self.__send_q, self.recv_q, debug=self.debug, sentinel = _sentinel)
    self.socket.start()
    # get the version once connected
    self.version   = self.__send('version')

  def connectMenu(self, devices):
    print("Select the Mirobot to connect to:")
    for i, device in enumerate(devices):
      print("  %i: %s" % (i+1, device['name']))
    try:
      choice = raw_input("Select a number:")
    except:
      choice = input("Select a number: ")
    return choice

  def autoConnect(self, id = None, interactive = False):
    try:
      res = request.urlopen("http://local.mirobot.io/devices.json").read()
    except:
      raise Exception("Could not connect to discovery server")

    try:
      devices = json.loads(str(res, 'utf-8'))
    except TypeError:
      devices = json.loads(res)

    print(devices)
    if interactive:
      choice = self.connectMenu(devices['devices'])
      print("Connecting to: %s" % devices['devices'][int(choice)-1]['name'])
      self.connect(devices['devices'][int(choice)-1]['address'])
    else:
      if id:
        filtered = [item for item in devices['devices'] if item['name'] == id]
        if len(filtered) == 0:
          raise Exception("No Mirobots found with id: %s" % id)
        elif len(filtered) == 1:
          # Connect to the only device we've found
          self.connect(filtered[0]['address'])
        else:
          raise Exception("Multiple Mirobots found with id: %s" % id)
      else:
        if len(devices['devices']) == 0:
          raise Exception("No Mirobots found")
        elif len(devices['devices']) == 1:
          # Connect to the only device we've found
          self.connect(devices['devices'][0]['address'])
        else:
          raise Exception("Too many Mirobots found to auto connect without specifying an ID")

  def errorNotify(self, on_error):
    self.__on_error = on_error

  def collideNotify(self, on_collide):
    enabled = bool(on_collide)
    self.__on_collide = on_collide
    self.__send('collideNotify', ('false','true')[enabled])

  def followNotify(self, on_follow):
    enabled = bool(on_follow)
    self.__on_follow = on_follow
    self.__send('followNotify', ('false','true')[enabled])

  def ping(self):
    return self.__send('ping')

  def uptime(self):
    return self.__send('uptime')

  def forward(self, distance):
    return self.__send('forward', distance, distance/20)

  def back(self, distance):
    return self.__send('back',    distance, distance/20)

  def left(self, degrees):
    return self.__send('left',    degrees,  degrees/20)

  def right(self, degrees):
    return self.__send('right',   degrees,  degrees/20)

  def penup(self):
    return self.__send('penup')

  def pendown(self):
    return self.__send('pendown')

  def beep(self, milliseconds = 500):
    return self.__send('beep',    milliseconds, milliseconds / 500)

  def collideState(self):
    return self.__send('collideState')

  def followState(self):
    return self.__send('followState')

  def disconnect(self):
    self.__send_q.put(_sentinel)

  def __send(self, cmd, arg = None, timeout = 1):
    # Assemble the message
    msg = {'cmd': cmd}
    if (arg is not None):
      msg['arg'] = str(arg)

    # Send the message and handle exceptions
    try:
      return self.__send_or_raise(msg, timeout)
    except Exception as x:
      if not self.__on_error:
        raise
      return self.__on_error(x, msg, timeout, self)

  def __send_or_raise(self, msg, timeout):
    msg_id = msg['id'] = self.generate_id()
    self.__send_q.put(msg)
    deadline = timeout + time.time()
    accepted = False
    while True:
      try:
        timeout = max(1, deadline - time.time())
        incoming = self.recv_q.get(block = True, timeout = timeout)
      except KeyboardInterrupt as e:
        self.disconnect()
        raise e
      except: # .get raises "Empty"
        if (accepted):
          raise IOError("Mirobot timed out awaiting completion of %r" % (msg,))
        raise IOError("Mirobot timed out awaiting acceptance of %r" % (msg,))

      try:
        rx_id = incoming.get('id','???')
        if rx_id != msg_id:
          if (rx_id == 'collide'):
            self.__collide(incoming)
            continue
          if (rx_id == 'follow'):
            self.__follow(incoming)
            continue
          raise IOError("Received message ID (%s) does not match expected (%s)" % (rx_id, msg_id))
        rx_status = incoming.get('status','???')
        if rx_status == 'accepted':
          accepted = True
        elif rx_status == 'complete':
          return incoming.get('msg',None)
        elif rx_status == 'notify':
          pass
        else:
          raise IOError("Received message status (%s) unexpected" % (rx_status,))
      finally:
        self.recv_q.task_done()

  def __collide(self, msg):
    if self.__on_collide:
      left  = msg['msg'] in ('both','left')
      right = msg['msg'] in ('both','right')
      self.__on_collide(left, right, msg, self)

  def __follow(self, msg):
    if self.__on_follow:
      state  = int(msg['msg'])
      self.__on_follow(state, msg, self)

  def generate_id(self):
    self.n = (self.n + 1) % 0x10000
    return '%s%04x' % (self.nonce, self.n)
