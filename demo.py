#!/usr/bin/env python

from mirobot import Mirobot
import sys

if len(sys.argv) > 1:
  host = sys.argv[1]
else:
  host = 'local.mirobot.io'

mirobot = Mirobot(host, debug=True)

mirobot.forward(100)
mirobot.back(100)
mirobot.penup()

mirobot.disconnect()