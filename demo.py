#!/usr/bin/env python

from mirobot import Mirobot
import sys, time

# this is an optional error handler for the mirobot.
def on_error(x, msg, timeout, bot):
  print('ERROR:')
  print(x)
  print(msg)
  print(timeout)
  print(bot)
  sys.exit()
  mirobot.disconnect()

# choose the Mirobot to connect to
if len(sys.argv) > 1:
  host = sys.argv[1]
else:
  host = 'local.mirobot.io'

# connect to Mirobot - there are a few different ways of doing this

# Use the host we specified on the command line
#mirobot = Mirobot(host, debug=True)

# Create a Mirobot instance
mirobot = Mirobot(debug=True)
# Autoconnect to a Mirobot on our network (there can be only one)
mirobot.autoConnect()

# Get a menu so we can select which Mirobot to connect to
#mirobot.autoConnect(interactive=True)

# Specify the id of the Mirobot we want to connect to
#mirobot.autoConnect(id='Mirobot-abcd')

print("Mirobot version: %s" % mirobot.version)

# set up error handling
mirobot.errorNotify(on_error)

mirobot.forward(100)
mirobot.right(90)
mirobot.back(100)
mirobot.penup()

while True:
  state = mirobot.collideState()
  if state == 'left':
    mirobot.back(100)
    mirobot.left(90)
  if state == 'right':
    mirobot.back(100)
    mirobot.right(90)
  else:
    mirobot.forward(10)
