# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""CoinBrawl Bot.

A Bot to farm https://www.coinbrawl.com/ a bitcoin faucet, knowing the site doesn't
pay I don't feel bad anymore.
"""
__version__ = '0.0.1'

import logging
from bot_logic import BotLogic
from ConfigParser import ConfigParser
from time import sleep

from pprint import pprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Our main entry for the bot, atm, this is just a test.

    Todo:
        * Farming routines will be handled differently in the future.

    """
    # used to grab the config for the bot
    config = ConfigParser()
    # should always be on the root folder of this script
    config.read('./config.ini')

    # Get the credentials from the config file
    user = config.get('Credentials', 'user')
    password = config.get('Credentials', 'password')

    coinBrawl = BotLogic(user, password)
    coinBrawl.auth()

    # testing out
    while True:
        while True:
            if coinBrawl.reset_stamina()['status'] is 'success':
                coinBrawl.get_stats()
                break
            sleep(5)

        battle_result = coinBrawl.battle_npc(5)
        print battle_result['message']
        if battle_result['type'] == 'success':
            while True:
                if coinBrawl.upgrade_stamina()['status'] is not 'success':
                    break

if __name__ == '__main__':
    main()

