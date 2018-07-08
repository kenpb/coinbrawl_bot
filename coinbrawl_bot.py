# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""CoinBrawl Bot.

A Bot to farm https://www.coinbrawl.com/ a bitcoin faucet.
"""
__version__ = '0.0.1'

import logging
import getopt, sys

from bot_logic import BotLogic
from ConfigParser import ConfigParser
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

npc_id = 0

def usage():
    print 'Usage: python ./coinbrawl_bot.py -h, --help | -f, --farm-stats <stamina | tokens | attack | defense> | -p, --pvp <win_percentage>'
    print '\nWill run a farm routine until interruption (spam ctrl-c).'
    print '\nNote:'
    print '\tThe PVP routine cannot reset the tokens due to the google captcha needed, reset them manually.'
    print '\nOptions:'
    print '\n-h, --help\t prints this message.'
    print '-f, --farm-stats upgrade stat routine.'
    print '-p, --pvp\t you optional number indicading the percentage of win agains our targets.'

def setup_robot():
    """Setup Robot.

    Creates an instance of the robot using the configuration from our root `config.ini` file.

    Returns:
        An authed instance of our bot.

    """
    # used to grab the config for the bot
    config = ConfigParser()
    # should always be on the root folder of this script
    config.read('./config.ini')

    # Get the credentials from the config file
    user = config.get('Credentials', 'user')
    password = config.get('Credentials', 'password')
    global npc_id
    npc_id = config.get('NPC', 'id')

    coinBrawl = BotLogic(user, password)
    coinBrawl.auth()
    # return the robot instance
    return coinBrawl

def main():
    """Our main entry for the bot.

    Todo:
        * Farming routines should be handled differently
        * Check code for more

    """
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hf:p:', ['help', 'farm-stats=', 'pvp='])
    except getopt.GetoptError as err:
        # print help information and exit:
        print err
        usage()
        sys.exit(2)

    if not opts:
        usage()
        sys.exit(2)

    for option, arg in opts:
        if option in ('-h', '--help'):
            # print the help
            usage()
            sys.exit()
        elif option in ('-f', '--farm-stats'):
            # Setup our robot instance
            coinBrawl = setup_robot()

            while True:
                while True:
                    # loop until we get the stamina reset
                    if coinBrawl.reset_stamina()['status'] is 'success':
                        coinBrawl.get_stats()
                        break
                    # Todo:
                    #   * The timer should be in the config too
                    sleep(5)

                # farm our target NPC
                battle_result = coinBrawl.battle_npc(int(npc_id))
                logger.info(battle_result['message'])
                if battle_result['type'] == 'success':
                    while True:
                        # we did upgrade the stamina
                        if arg == 'stamina':
                            if coinBrawl.upgrade_stamina()['status'] is not 'success':
                                # we didn't
                                break
                        # we did upgrade the tokens
                        if arg == 'tokens':
                            if coinBrawl.upgrade_tokens()['status'] is not 'success':
                                # we didn't
                                break
                        # we did upgrade the attack
                        if arg == 'attack':
                            if coinBrawl.upgrade_attack()['status'] is not 'success':
                                # we didn't
                                break
                        # we did upgrade the defense
                        if arg == 'defense':
                            if coinBrawl.upgrade_defense()['status'] is not 'success':
                                # we didn't
                                break
                        if arg == 'gold':
                            # do nothing. cuz, its just loops away
                            break
                    # wait 500ms between calls
                    sleep(5/10)
        elif option in ('-p', '--pvp'):
            # setup the bot instance
            CoinBrawl = setup_robot()
            # Todo:
            #   * The argument is not optional by default (getopt)
            if arg is not None: above_win_rate = True
            while True:
                # farm player non-stop
                if not coinBrawl.battle_players(above_win_rate=above_win_rate, win_rate=arg):
                    # untested, but should break (return false) when we run out of tokens
                    break
                # 6 https requests per batch, throttle it a little
                sleep(1)
        else:
            # print help information and exit:
            usage()
            sys.exit(2)

if __name__ == '__main__':
    main()

