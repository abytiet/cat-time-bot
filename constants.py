"""
Cat Bot constants
"""
import os
from dotenv import load_dotenv

load_dotenv()

COMMANDS = ['~commands', '~pet', '~feed', '~meow', '~stats', '~play', '~scold', '~adopt', '~abandon', '~name', '~cps',
            '~fact', '~rehome']

STATUSES = ["meowing", "nyaaa", ":3", ":3c", "doing cat things", "~commands", "~adopt me"]

HUNGRY = ["i am going to die please feed me some food", "I'M SO HUNGWYYYY",
          "please feed me....", "my tummy is gwumbling...", "I'M HUNGRY!!!"]

LONELY = ["i am so lonely no one cares about me", "please give me some attention...", "do you even care about me?!",
          "i wish i had someone to play with me", "DOES ANYONE EVEN CARE? T_T"]

DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

MONGODB_TOKEN = os.environ['MONGODB']
