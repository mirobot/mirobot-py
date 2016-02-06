#!/usr/bin/env python

from mirobot import Mirobot
import sys

# this is an optional error handler for the mirobot.

def on_error(bot, msg, timeout, x):
  print('ERROR:')
  print(bot)
  print(msg)
  print(timeout)
  print(x)

if len(sys.argv) > 1:
  host = sys.argv[1]
else:
  host = 'local.mirobot.io'

mirobot = Mirobot(host, debug=True)
print(mirobot.state)

mirobot.on_error = on_error

mirobot.forward(100)
mirobot.back(100)
mirobot.penup()

mirobot.disconnect()