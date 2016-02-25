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

# this handles collisions
def on_collide(left, right, msg, bot):
  print('COLLISION:')
  print(left)
  print(right)
  print(msg)
  print(bot)

# this handles changes in the line following sensor
def on_follow(state, msg, bot):
  print('FOLLOW:')
  print(state)
  print(msg)
  print(bot)

# choose the Mirobot to connect to
if len(sys.argv) > 1:
  host = sys.argv[1]
else:
  host = 'local.mirobot.io'

# connect
mirobot = Mirobot(host, debug=True)
print("Mirobot version: %s" % mirobot.version)

# set up error handling
mirobot.errorNotify(on_error)

# These commands set up the collision and line following handling
#mirobot.collideNotify(on_collide)
#mirobot.followNotify(on_follow)

mirobot.forward(100)
mirobot.right(90)
mirobot.back(100)
mirobot.penup()

mirobot.disconnect()