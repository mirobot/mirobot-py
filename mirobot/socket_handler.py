import threading
import websocket
import json
import logging
logging.basicConfig()

class SocketHandler(threading.Thread):
  def __init__(self, host, send_q, recv_q, debug=False, sentinel=None):
    super(SocketHandler, self).__init__()
    self.debug = debug
    self.send_q = send_q
    self.recv_q = recv_q
    self._sentinel = sentinel
    self.ready = False

    def on_message(ws, message):
      self.recv_q.put(json.loads(message))
      print(message)

    def on_error(ws, error):
      print(error)

    def on_close(ws):
      # TODO: implement reconnection strategy
      pass

    def on_open(ws):
      self.ready = True;

    self.ws = websocket.WebSocketApp('ws://%s:8899/websocket' % host,
      on_message = on_message,
      on_error = on_error,
      on_close = on_close,
      on_open = on_open)

    # Run the WebSocket handler in its own thread
    def run_ws():
      self.ws.run_forever()

    threading.Thread(target=run_ws).start()

    if (self.debug):
      print('opened socket to %s:%d' % (host, 8899))

  def run(self):
    while True:
      # Pull new messages to send off the queue
      if self.send_q.qsize() > 0 and self.ready == True:
        msg = self.send_q.get()
        # Check if we're being told to shut down
        if msg is self._sentinel:
          self.ws.close()
          break
        if self.debug: print("Tx: " + json.dumps(msg))
        msg_to_send = json.dumps(msg) + "\r\n"
        # Send the message
        self.ws.send(msg_to_send)
        self.send_q.task_done()
