import threading
import socket, select
import json
import sys

class SocketHandler(threading.Thread):
  def __init__(self, host, send_q, recv_q, debug=False, sentinel=None):
    super(SocketHandler, self).__init__()
    self.send_q = send_q
    self.recv_q = recv_q
    self._sentinel = sentinel
    self.stoprequest = threading.Event()
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.connect((host, 8899))
    self.sock.setblocking(0)
    self.recv_buff = ''
    self.debug = debug

  def run(self):
    while True:
      # Pull new messages to send off the queue
      if self.send_q.qsize() > 0:
        msg = self.send_q.get()
        # Check if we're being told to shut down
        if msg is self._sentinel:
          return self.sock.close()
        if self.debug: print("Transmitted: " + json.dumps(msg))
        msg_to_send = json.dumps(msg) + "\r\n"
        # Send the message
        if sys.version_info.major == 2:
          self.sock.sendall(bytes(msg_to_send))
        else:
          self.sock.sendall(bytes(msg_to_send, 'utf-8'))
        
      # Check to see if we have new data from the socket
      self._recv()

  def _recv(self):
    read_sockets,_,_ = select.select([self.sock],[],[], 0.05)
    if len(read_sockets) == 1:
      # There's data in the buffer so let's process it
      self.recv_buff += self.sock.recv(1024).decode('utf-8')
      # Look for the carriage return message delimiter
      splitstr = self.recv_buff.split("\r\n")
      if len(splitstr) > 1:
        msg = json.loads(splitstr[0])
        if self.debug: print("Received: " + splitstr[0])
        self.recv_buff = self.recv_buff[len(splitstr[0]) + 2:]
        # Send out the parsed message
        self.recv_q.put(msg)
