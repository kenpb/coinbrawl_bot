# -*- coding: utf-8 -*-
"""Encore.

Our HTTP helper for the interaction with the site.
"""

import logging
from fake_useragent import UserAgent
from requests import Session, exceptions, utils
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
        self.headers = { 'User-Agent': user_agent.random }

    def expand_headers(self, headers):
        """This will update the headers globally.
        
        This affects all the requests after the invocation.
        """
        self.headers.update(headers)

    @retry(max_retries=100, timeout=15)
    def get(self, url, headers={}):
        """A simple GET request.

        Args:
            url: The requested URL.
            headers: Any custom headers we need to supply.

        Returns:
            A request object.

        """
        # expand our headers dictionary for this request
        request_headers = self.headers
        request_headers.update(headers)
        # do the request
        current_request = self.session.get(url, headers=request_headers)
        # throw on 404, 500 and other common HTTP errors
        current_request.raise_for_status()
        # return the raw request object
        return current_request

    @retry(max_retries=100, timeout=15)
    def post(self, url, data={}, headers={}):
        """A simple POST request.

        Args:
            url: The requested URL.
            data: The payload to be posted.
            headers: Any custom headers we need to supply.

        Returns:
            A request object.

        """
        # expand our headers dictionary for this request
        request_headers = self.headers
        request_headers.update(headers)
        # do the request
        current_request = self.session.post(url, data=data, headers=request_headers)
        # throw on 404, 500 and other common HTTP errors
        current_request.raise_for_status()
        # return the raw request object
        return current_request
