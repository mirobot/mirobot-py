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

  def forward(self, distance):
    self.__send({'cmd':'forward', 'arg':str(distance)}, distance/20)

  def back(self, distance):
    self.__send({'cmd':'back', 'arg':str(distance)}, distance/20)

  def left(self, degrees):
    self.__send({'cmd':'left', 'arg':str(degrees)}, degrees/20)

  def right(self, degrees):
    self.__send({'cmd':'right', 'arg':str(degrees)}, degrees/20)

  def penup(self):
    self.__send({'cmd':'penup'}, 1)

  def pendown(self):
    self.__send({'cmd':'pendown'}, 1)

  def beep(self, milliseconds):
    self.__send({'cmd':'beep', 'arg':str(milliseconds)}, milliseconds / 500)

  def disconnect(self):
    self.__send_q.put(_sentinel)

  def __send(self, msg, timeout):
    msg_id = msg['id'] = self.generate_id()
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
      rx_id = incoming.get('id','???')
      if rx_id != msg_id:
        raise IOError("Received message ID (%s) does not match expected (%s)" % (rx_id, msg_id))
      rx_stat = incoming.get('status','???')
      if rx_stat == 'accepted':
        accepted = True
      elif rx_stat == 'complete':
        return
      else:
        raise IOError("Received message status (%s) unexpected" % (rx_stat,))

  def generate_id(self):
    self.n = (self.n + 1) % 0x10000
    return '%s%04x' % (self.nonce, self.n)
