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
    self.on_error = None

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
      if not self.on_error:
        raise
      return self.on_error(self, msg, timeout, x)

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
          raise IOError("Received message ID (%s) does not match expected (%s)" % (rx_id, msg_id))
        rx_stat = incoming.get('status','???')
        if rx_stat == 'accepted':
          accepted = True
        elif rx_stat == 'complete':
          return None
        else:
          raise IOError("Received message status (%s) unexpected" % (rx_stat,))
      finally:
        self.recv_q.task_done()

  def generate_id(self):
    self.n = (self.n + 1) % 0x10000
    return '%s%04x' % (self.nonce, self.n)
