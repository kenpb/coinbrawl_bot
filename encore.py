# -*- coding: utf-8 -*-
"""Encore.

Our HTTP helper for the interaction with the site.
"""

import logging
from fake_useragent import UserAgent
from requests import Request, Session, exceptions, utils
from time import sleep
from retryer import retry

logger = logging.getLogger(__name__)

class Encore():
    """Encore.

    Provides a class wrapper around the requests module, I'll be using this to
    handle the requests done to the page.

    Todo:
        * I should allow a proxy in this too
        * Should check for the 302 URL and relog if its sig_in https://stackoverflow.com/questions/20475552/python-requests-library-redirect-new-url

    """
    def __init__(self):
        # grab a random user agent for the requests
        user_agent = UserAgent()
        # initialize the session for the cookie handling
        self.session = Session()
        # initialize the default headers with the agent
        self.session.headers.update({ 'User-Agent': user_agent.random })
        # site root
        self.base_url = 'https://www.coinbrawl.com'

    def expand_headers(self, headers):
        """This will update the headers globally.
        
        This affects all the requests after the invocation.
        """
        self.session.headers.update(headers)

    def check_session(self, request, func, timeout=10):
        """Makes sure we are still logged.
        
        Checks whether the `302` redirection is to `/users/sign_in`, in which case it will run a function until,
        and resend the request until it's not longer the case, sleeping 10 seconds every retry.

        Args:
            request (object): A prepared request.
            funct (function): The function that will run in case of session expiration.
            timeout (int, optional): Our delay between retries.

        Todo:
            * Should not loop forever

        """
        # we'll alwayas have a history since we'll get a redirect most of the time
        logger.info('Checking session...')
        while(True):
            response = self.session.send(request)
            if response.history:
                logger.debug('Request was redirected...')
                # we'll check all the subsequent redirects
                for resp in response.history:
                    # and look for the login page
                    if (resp.url == self.base_url + '/users/sign_in'):
                        logger.info('Session expired...')
                        func()
                        sleep(timeout)
                        continue
                    else:
                        logger.info('Still logged...')
                        return response

    @retry(max_retries=100, timeout=15)
    def get(self, url, headers={}, check_session=False, func=None):
        """A simple GET request.

        Args:
            url (str): The requested URL.
            headers (dict): Any custom headers we need to supply.
            check_session (bool, optional): This request will run the function provided int `func` argument if
                this flag is True and a 302 happens to redirect to `/users/sign_in`, defaults to False.
            func (function, optional): The function that must be run if a 302 redirects to `/users/sign_in`,
                defaults to False.

        Returns:
            A request object.

        """
        # make sure we provide a function to run in case our session expired
        if (check_session and func == None):
            raise ValueError('A function must be provided if the `check_session` flag is True')

        # prepare the request add extra headers if any
        request = Request('GET', url, headers=headers)
        prepared_request = self.session.prepare_request(request)
        # our response object
        current_request = None

        # we will pass the prepared request to the check session method if the flag is up
        if (check_session):
            # else we will simply do the request as usual
            current_request = self.check_session(prepared_request, func)
        else:
            # else we will simply do the request as usual
            current_request = self.session.send(prepared_request)

        # throw on 404, 500 and other common HTTP errors
        current_request.raise_for_status()
        # return the raw request object
        return current_request

    @retry(max_retries=100, timeout=15)
    def post(self, url, data={}, headers={}, check_session=False, func=None):
        """A simple POST request.

        Args:
            url (str): The requested URL.
            data (dict): The payload to be posted.
            headers (dict): Any custom headers we need to supply.

        Returns:
            A request object.

        """
        # make sure we provide a function to run in case our session expired
        if (check_session and func == None):
            raise ValueError('A function must be provided if the `check_session` flag is True')

        # prepare the request add extra headers if any
        request = Request('POST', url, data=data, headers=headers)
        prepared_request = self.session.prepare_request(request)
        # our response object
        current_request = None

        # we will pass the prepared request to the check session method if the flag is up
        if (check_session):
            # else we will simply do the request as usual
            current_request = self.check_session(prepared_request, func)
        else:
            # else we will simply do the request as usual
            current_request = self.session.send(prepared_request)

        # throw on 404, 500 and other common HTTP errors
        current_request.raise_for_status()
        # return the raw request object
        return current_request
