"""
Cat Bot constants
"""
import os


COMMANDS = ['~commands', '~pet', '~feed', '~meow', '~stats', '~play', '~scold', '~adopt', '~abandon', '~name', '~cps',
            '~fact', '~rehome']

STATUSES = ["meowing", "nyaaa", ":3", ":3c", "doing cat things", "~commands", "~adopt me"]

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

MONGODB_TOKEN = os.environ['MONGODB']