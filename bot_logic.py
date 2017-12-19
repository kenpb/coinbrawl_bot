# -*- coding: utf-8 -*-
"""Bot Logic.

Provides all the logic for the routines and requests related to the bot.
"""

import logging
from re import search, findall
from json import loads
from string import replace
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
        self.base_url = self.encore.base_url
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
        auth_token_regex = r'name="authenticity_token" type="hidden" value="(.*?)" \/>'
        # the arena token regex, grabs the token from the raw JS of the React app
        arena_token_regex = r'battles: \[{"key":"(.*?)",'
        # the csrf token for the headers, embedded in the head and meta tags
        csrf_token_regex = r'meta content="(.*?)" name="csrf-token"'
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
        logger.info('Grabbing arena token...')
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

            Note:
                Must be run once every cycle since the attributes above are necessary for the upgrade
                and farm functions.

        """
        logger.info('Getting the current stats...')
        # get the data from the API endpoint
        stats_json = self.encore.get(self.base_url + '/api/quick_stats').json()
        logger.debug(stats_json)
        # set the stats accordingly
        # the response looks like `current_amount/limit` being both, current amount and limit, numbers
        self.friendly_stamina = stats_json['friendly_stamina'].split('/')[1]
        self.friendly_tokens = stats_json['friendly_tokens'].split('/')[1]
        self.gold = stats_json['gold']

    def reset_stamina(self):
        """Resets the current player stamina so we can engage again.

        The `reset stamina` action is subject to a timer, this timer increases acording to the
        players LVL.

        Todo:
            * Just because the request went through it doesn't mean it was successful, handle this

        """
        logger.info('Reseting stamina...')
        logger.debug('Preparing post payload...')
        # prepare the payload, the authenticity token here is the one we get after the login screen
        # it's embedded in the meta of the HTML page
        post_data = { 'utf8' : '✓', 'authenticity_token': self.csrf_token, 'commit': 'Submit' }
        # post the data to the endpoint
        logger.debug('Sending request...')
        # will relog if our session expired
        response = self.encore.post(self.base_url + '/character/regenerate_stamina', data=post_data, check_session=True, func=self.auth)
        # this will be in the page if we got a successfull reset
        success_regex = r'Success\! You have gained more stamina\.'
        result = search(success_regex, response.text)

        if result is not None and result.group(0) is not None:
            logger.info('The stamina has been reset successfully...')
            return { 'status': 'success', 'response': response }
        else:
            logger.info('Could not reset stamina something went wrong...')
            return { 'status': 'error', 'response': response }

    def upgrade_stamina(self, allow_redirects=True):
        """Upgrades the defense points.
        
        Args:
            allow_redirects (bool): if false it will not redirect or get the status of the action but will save a request
                may be useful when we are just upgrading non-stoping.

        Returns:
            Returns a dictionary with the status and the response object:
                `success`: Will mean everything went fine and the upgraded was successful.
                `unknown`: `allow_redirects` is `False` and our action result is unknown.
                `fail`: There was an error, most certainly not enough gold.
            
        """
        logger.info('Upgrading stamina...')
        response = self.encore.get(self.base_url + '/upgrades/maximum_stamina', check_session=True, func=self.auth, allow_redirects=allow_redirects)

        if not allow_redirects:
            return { 'status': 'unknown', 'response': response }

        success_regex = r'You have successfully upgraded your maximum stamina by 1\!'

        result = search(success_regex, response.text)

        if result is not None and result.group(0) is not None:
            logger.info('The stamina has been upgraded successfully...')
            return { 'status': 'success', 'response': response }
        else:
            logger.info('Could not upgrade stamina, something went wrong...')
            return { 'status': 'error', 'response': response }


    def upgrade_tokens(self, allow_redirects=True):
        """Upgrades the defense points.
        
        Args:
            allow_redirects (bool): if false it will not redirect or get the status of the action but will save a request
                may be useful when we are just upgrading non-stoping.

        Returns:
            Returns a dictionary with the status and the response object:
                `success`: Will mean everything went fine and the upgraded was successful.
                `unknown`: `allow_redirects` is `False` and our action result is unknown.
                `fail`: There was an error, most certainly not enough gold.
            
        """
        request = self.encore.get(self.base_url + '/upgrades/maximum_tokens')

        if not allow_redirects:
            return { 'status': 'unknown', 'response': response }

        success_regex = r'You have successfully upgraded your maximum tokens by 1\!'

        result = search(success_regex, response.text)

        if result is not None and result.group(0) is not None:
            logger.info('The tokens has been upgraded successfully...')
            return { 'status': 'success', 'response': response }
        else:
            logger.info('Could not upgrade tokens, something went wrong...')
            return { 'status': 'error', 'response': response }



    def upgrade_attack(self, allow_redirects=True):
        """Upgrades the defense points.
        
        Args:
            allow_redirects (bool): if false it will not redirect or get the status of the action but will save a request
                may be useful when we are just upgrading non-stoping.

        Returns:
            Returns a dictionary with the status and the response object:
                `success`: Will mean everything went fine and the upgraded was successful.
                `unknown`: `allow_redirects` is `False` and our action result is unknown.
                `fail`: There was an error, most certainly not enough gold.
            
        """
        request = self.encore.get(self.base_url + '/upgrades/attack')

        if not allow_redirects:
            return { 'status': 'unknown', 'response': response }

        success_regex = r'You have successfully upgraded your attack\!'

        result = search(success_regex, response.text)

        if result is not None and result.group(0) is not None:
            logger.info('The attack has been upgraded successfully...')
            return { 'status': 'success', 'response': response }
        else:
            logger.info('Could not upgrade attack something went wrong...')
            return { 'status': 'error', 'response': response }


    def upgrade_defense(self, allow_redirects=True):
        """Upgrades the defense points.
        
        Args:
            allow_redirects (bool): if false it will not redirect or get the status of the action but will save a request
                may be useful when we are just upgrading non-stoping.

        Returns:
            Returns a dictionary with the status and the response object:
                `success`: Will mean everything went fine and the upgraded was successful.
                `unknown`: `allow_redirects` is `False` and our action result is unknown.
                `fail`: There was an error, most certainly not enough gold.

        """
        request = self.encore.get(self.base_url + '/upgrades/defense')

        if not allow_redirects:
            return { 'status': 'unknown', 'response': response }

        success_regex = r'You have successfully upgraded your defense\!'

        result = search(success_regex, response.text)

        if result is not None and result.group(0) is not None:
            logger.info('The defense has been upgraded successfully...')
            return { 'status': 'success', 'response': response }
        else:
            logger.info('Could not upgrade defese something went wrong...')
            return { 'status': 'error', 'response': response }

    def battle_players(self, above_win_rate=False, win_rate=None):
        """Engages in battle with another player.

        Args:
            above_win_rate (bool): only fight players that we have with certain amount of winning.
            win_rate (int): if `above_win_rate` is True, this will be the minimun win_rate required to be challenged.

        Returns:
            `False` if there are no more tokens, True if everything (beside the fight results) went fine.

        Todo:
            * Should do more with the battle results

        """
        if (above_win_rate and win_rate == None):
            raise ValueError('You must specify a win percentage if the `above_win_rate` flag is True')

        available_battles = self.encore.get(self.base_url + '/api/available_battles').json()
        logger.info('Fighting players...')
        for battle in available_battles:
            key = battle['key'] # current arena key, but lets grab it anyways lol
            defender_username = battle['defender_username']
            defender_id = battle['defender_id'] # our farm enemy id
            defender_win_chance = replace(battle['percentage_chance'], '%', '')

            #if (defender_win_chance <= 40) return // return if we have less than this chance of winning

            post_data = { 'battle[defender_id]'	: defender_id, 'token' : key }
            # post the data to the endpoint
            logger.debug('Sending battle request...')
            # will relog if our session expired
            battle_result = self.encore.post(self.base_url + '/battles', data=post_data).json()

            # should handle the win rate or something else here <--

            # if we run out of tokens we should false the return here
            if battle_result['message'] == 'Sorry, you are out of tokens! You can get more tokens on the \'Character\' page.':
                return False

        return True

    def battle_npc(self, id=0):
        """Engages in battle with an NPC.

        Args:
            id (int): The number (according to list position) of the corresponding NPC to battle, as in:
                0: `dummy: 0/0`
                1: `village_idiot: 10/10`
                2: `swordsman: 20/20` 
                3: `wandering_wizzard: 250/250`
                4: `black_knight: 500/500`
                5: `cyrstal_dragon: 1000/1000`

        Returns:
            The original JSON from the response containing `type` which indicates the status of the fight, and `message`
            which gives a larger description (we care about it in the error cases at least)

        """
        npc_ids = ['dummy', 'village_idiot', 'swordsman', 'wandering_wizard', 'black_knight', 'crystal_dragon']
        post_data = { 'defender_id' : npc_ids[id], 'token' : self.arena_token, 'stamina' : self.friendly_stamina }
        return self.encore.post(self.base_url + '/battles/fight_npc', data=post_data).json()
