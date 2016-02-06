#!/usr/bin/env python

from mirobot import Mirobot
import sys

# this is an optional error handler for the mirobot.

def on_error(x, msg, timeout, bot):
  print('ERROR:')
  print(x)
  print(msg)
  print(timeout)
  print(bot)

def on_collide(left, right, msg, bot):
  print('COLLISION:')
  print(left)
  print(right)
  print(msg)
  print(bot)

def on_follow(state, msg, bot):
  print('FOLLOW:')
  print(state)
  print(msg)
  print(bot)

if len(sys.argv) > 1:
  host = sys.argv[1]
else:
  host = 'local.mirobot.io'

mirobot = Mirobot(host, debug=True)
print(mirobot.state)

mirobot.on_error   = on_error
mirobot.on_collide = on_collide
mirobot.on_follow  = on_follow

mirobot.forward(100)
mirobot.back(100)
mirobot.penup()

mirobot.disconnect()