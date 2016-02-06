try:
  from queue import Queue
except ImportError:
  from Queue import Queue
from mirobot.socket_handler import SocketHandler
import time
import string
import random

_sentinel = object()

class Mirobot:
  def __init__(self, address, debug = False):
    self._debug = debug
    self.__send_q = Queue()
    self.recv_q = Queue()
    self.socket = SocketHandler(address, self.__send_q, self.recv_q, debug=debug, sentinel = _sentinel)
    self.nonce  = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4))
    self.n      = 0
    self.socket.start()
    # callbacks
    self.__on_error    = None
    self.__on_collide  = None
    self.__on_follow   = None
    #
    self.version   = self.__send('version')
    self.hwversion = self.__send('hwversion')
    ###
    for k in ('ping','collideState','followState'
              #'uptime', not supported?
              ):
      print(self.__send(k))

    self.collideNotify()
    self.followNotify(False)



  def errorNotify(self, on_error):
    self.__on_error = on_error

  def collideNotify(self, on_collide):
    enabled = bool(on_collide)
    self.__on_collide = on_collide
    self.__send('collideNotify',
                    ('false','true')[enabled])

  def followNotify(self, on_follow):
    enabled = bool(on_follow)
    self.__on_follow = on_follow
    self.__send('followNotify',
                    ('false','true')[enabled])

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

  def beep(self, milliseconds):
    return self.__send('beep',    milliseconds, milliseconds / 500)

  def disconnect(self):
    self.__send_q.put(_sentinel)

  def __send(self, cmd, arg = None, timeout = 1):
    msg = {'cmd': cmd, 'id': self.generate_id()}
    if (arg is not None):
      msg['arg'] = str(arg)

    try:
      return self.__send_or_raise(msg, timeout)
    except Exception as x:
      if not self.__on_error:
        raise
      return self.__on_error(x, msg, timeout, self)

  def __send_or_raise(self, msg, timeout):
    if self._debug:
      print('<< %r' % msg)
    self.__send_q.put(msg)
    deadline = timeout + time.time()
    accepted = False
    while True:
      try:
        timeout = max(1, deadline - time.time())
        if self._debug:
          print(timeout)
        incoming = self.recv_q.get(block = True, timeout = timeout)
      except: # .get raises "Empty"
        if (accepted):
          raise IOError("Mirobot timed out awaiting completion of %r" % (msg,))
        raise IOError("Mirobot timed out awaiting acceptance of %r" % (msg,))

      if self._debug:
        print(incoming)
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
        rx_stat = incoming.get('status','???')
        if rx_stat == 'accepted':
          accepted = True
        elif rx_stat == 'complete':
          return incoming.get('msg',None)
        else:
          raise IOError("Received message status (%s) unexpected" % (rx_stat,))
      finally:
        self.recv_q.task_done()

  def __collide(self, msg):
    if self.__on_collision:
      left  = msg['msg'] in ('both','left')
      right = msg['msg'] in ('both','right')
      self.__on_collision(left, right, msg, self)

  def __follow(self, msg):
    if self.__on_follow:
      state  = int(msg['msg'])
      self.__on_follow(state, msg, self)

  def generate_id(self):
    self.n = (self.n + 1) % 0x10000
    return '%s%04x' % (self.nonce, self.n)

"""
        immediate commands
    safe


    interesting
calibrateMove
calibrateTurn
collideNotify          # enable asynchronous collision-detect notification
followNotify           # enable asynchronous line-follow notification
moveCalibration
reset
sethwversion
slackCalibration
turnCalibration
pause                  #
resume                 # mess with motors
stop                   #


       slow commands
back
beep
calibrateSlack
collide                # set collide mode
follow                 # set line follow mode
forward
left
pendown
penup
right


"""
