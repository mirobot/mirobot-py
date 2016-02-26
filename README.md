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

    # Beep for a second
    mirobot.beep(1000)

    # Print the state of the collision sensors
    print(mirobot.collideState())

    # Print the state of the line following sensors
    print(mirobot.followState())

    # Disconnect from Mirobot
    mirobot.disconnect()

It currently runs on both Python 2 and Python 3. Currently all commands are synchronous.

## Installing

You can use `pip` to install the Mirobot library on your system:

    pip install mirobot

You may need to run this as a super user if you get an error, in which case on Mac or Linux, run:

    sudo pip install mirobot
