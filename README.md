# Mirobot Python Library

This is a library to control your Mirobot from the Python programming language. It has a simple API which mirrors the basic movements that Mirobot can do. Here's a sample program that runs through the API:

    from mirobot import Mirobot
    
    # Connect to Mirobot
    mirobot = Mirobot('local.mirobot.io')

    # Put the pen down
    mirobot.pendown()

    # Move forward 100mm
    mirobot.forward(100)

    # Move back 100mm
    mirobot.back(100)

    # Turn left 45 degrees
    mirobot.left(45)

    # Turn right 45 degrees
    mirobot.right(45)

    # Lift the pen up
    mirobot.penup()

    # Disconnect from Mirobot
    mirobot.disconnect()

It currently runs on Python 3