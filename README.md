# Mirobot Python Library

This is a library to control your Mirobot from the Python programming language. It has a simple API which mirrors the basic movements that Mirobot can do. Here's a sample program that runs through the API:

    from mirobot import Mirobot
    
    # Connect to Mirobot
    mirobot = Mirobot()
    mirobot.autoConnect()

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

There are a few different ways of connecting to Mirobot:

Specify the IP address or hostname manually:

    mirobot = Mirobot('local.mirobot.io')

If you're running a v2 or greater Mirobot with firmware version at or greater than 2.0.9 you can also use the discovery mechanism to auto connect which saves having to figure out where it is on your network. If you only have one Mirobot on your network, you can just do this:

    mirobot = Mirobot()
    mirobot.autoConnect()

If you have more than one you can either specify the ID of the Mirobot to connect to that one:

    mirobot = Mirobot()
    mirobot.autoConnect('Mirobot-abcd')

Or you can use the interactive mode to select which one to connect to:

    mirobot = Mirobot()
    mirobot.autoConnect(interactive=True)
    
    >>> Select the Mirobot to connect to:
    >>>   1: Mirobot-ad43
    >>>   2: Mirobot-ea51
    >>> Select a number:

It currently runs on both Python 2 and Python 3. Currently all commands are synchronous.

## Installing

You can use `pip` to install the Mirobot library on your system:

    pip install mirobot

You may need to run this as a super user if you get an error, in which case on Mac or Linux, run:

    sudo pip install mirobot
