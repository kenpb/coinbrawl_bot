# -*- coding: utf-8 -*-
"""Bot Logic.

Provides all the logic for the routines and requests related to the bot.
"""

import logging
from re import search, findall
from json import loads
from encore import Encore

logger = logging.getLogger(__name__)

class BotLogic():
    """BotLogic.

    A class to handle the bot logic.
    """
    def __init__(self, user, password):
        # initialize the HTTP class
        self.encore = Encore()
        # the site's url
        self.base_url = 'https://www.coinbrawl.com'
        # user credentials
        self.user = user
        self.password = password

    def auth(self):
        """Logs into the site and sets the following attributes:

            arena_token (str): A token embedded in the fighting UI, it's used as payload
                when doing NPC and PVP related battles.

            csrf_token (str): This token is different from the one used in the login screen
                it's used in the request headers to avoid csrf attacks and it's also required to
                do actual requests to the API since its validated by the server.
        """
        logger.info('Starting login process...')
        # the login endpoint uses an `authenticity_token` for it's request
        auth_token_regex = 'name="authenticity_token" type="hidden" value="(.*?)" \/>'
        # the arena token regex, grabs the token from the raw JS of the React app
        arena_token_regex = 'battles: \[{"key":"(.*?)",'
        # the csrf token for the headers, embedded in the head and meta tags
        csrf_token_regex = 'meta content="(.*?)" name="csrf-token"'
        # do a request to get the login page
        logger.info('Requesting login page...')
        login_html = self.encore.get(self.base_url + '/users/sign_in').text
        # grab the token from the form
        logger.info('Grabbing authenticity token...')
        self.auth_token = search(auth_token_regex, login_html).group(1)
        logger.debug('Got %s...', self.auth_token)
        # the payload to be posted
        logger.info('Login into the site...')
        post_data = { 'utf8' : '✓', 'authenticity_token': self.auth_token, 'user[email]' : self.user, 'user[password]': self.password, 'commit': 'Sign+in' }
        auth_request = self.encore.post(self.base_url + '/users/sign_in', data=post_data)
        logger.info('Login succesufully...')
        # grab the current arena token from the response HTML (we should be logged by now)
        logger.info('Grabbing  arena token...')
        self.arena_token = search(arena_token_regex, auth_request.text).group(1)
        logger.debug('Got %s...', self.arena_token)
        # grab the new csrf token from the meta tag
        logger.info('Grabbing csrf token...')
        self.csrf_token = search(csrf_token_regex, auth_request.text).group(1)
        logger.debug('Got %s...', self.csrf_token)
        # set the csrf token in the headers
        self.encore.expand_headers({ 'X-CSRF-Token': self.csrf_token })

    def get_stats(self):
        """Gets the stats for the current player and sets the following attributes:

            friendly_stamina (number): The amount of stamina, a stat to battle NPCs if the stamina
                is 0 we cannot fight NPCs.

            friendly_tokens (number): Current amount of tokens, this are PVP tokens and allow to
                engage another players, one token is consumed by battle.
        """
        # get the data from the API endpoint
        stats_json = self.encore.get(self.base_url + '/api/quick_stats').json()
        # set the stats accordingly
        # the response looks like `current_amount/limit` being both, current amount and limit, numbers
        self.friendly_stamina = stats_json['friendly_stamina'].split('/')[1]
        self.friendly_tokens = stats_json['friendly_tokens'].split('/')[1]

    def reset_stamina(self):
        """Resets the current player stamina so we can engage again.

        The `reset stamina` action is subject to a timer, this timer increases acording to the
        players LVL.

        Todo:
            * Just because the request went through it doesn't mean it was successful, handle this

        """
        # prepare the payload, the authenticity token here is the one we get after the login screen
        # it's embedded in the meta of the HTML page
        logger.info('Reseting stamina...')
        logger.debug('Preparing post payload...')
        post_data = { 'utf8' : '✓', 'authenticity_token': self.csrf_token, 'commit': 'Submit' }
        # post the data to the endpoint
        logger.debug('Sending request...')
        request = self.encore.post(self.base_url + '/character/regenerate_stamina', data=post_data)
        logger.info('The stamina has been reset successfully...')

    def upgrade_stamina():
        """
        Todo:
            * should check for /You have successfully upgraded your maximum stamina by 1\!/g
        """
        request = self.encore.get(self.base_url + '/upgrades/maximum_stamina', data=post_data)

    def upgrade_tokens():
        """
        Todo:
            * should check for /You have successfully upgraded your maximum tokens by 1\!/g
        """
        request = self.encore.get(self.base_url + '/upgrades/maximum_tokens', data=post_data)

    def upgrade_attack():
        """
        Todo:
            * should check for /You have successfully upgraded your attack\!/g
        """
        request = self.encore.get(self.base_url + '/upgrades/attack', data=post_data)

    def upgrade_defense():
        """
        Todo:
            * should check for /You have successfully upgraded your defense\!/g
        """
        request = self.encore.get(self.base_url + '/upgrades/defense', data=post_data)
