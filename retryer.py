# -*- coding: utf-8 -*-
"""Retryer.

A simple module with ``retryer``, a decorator that re-runs the decorated
function again after a sleep (blocking the current thread) in case of exception
during it's excecution.
"""

import logging
from time import sleep

logger = logging.getLogger(__name__)

class NetworkError(RuntimeError):
    pass

def retry(max_retries=10, timeout=10, incremental=False):
    """Decorator to retry web requests in case of failure.

    This decorator must be applied to all http requests. Example::

        @retryer(max_retries=100, timeout=15)
        def handle_my_custom_request(json):
            request = requests.get('https://www.google.com/)
            return request.text

    :param max_retries: The number of tries after a failed request.
    :param timeout: The timeout between requests, do not retry immediatly after a failure so the service or
                    error can be addressed by the source. Example::
                    
            Using the code snippet above you'll get a 15 second delay on the in every retry if the request fails.

    :param incremental: The timeout will increase according to the number of retries that have been done.Example::
                    
            Using the code snippet above you'll get a 15 second delay on the first retry, 30 in the second and so on,
            if the request fails.
    """
    def wrap(func):
        def inner(*args, **kwargs):
            for i in range(1, max_retries + 1):
                try:
                    # Run the decorated function
                    logger.debug('Running function %s...', func.func_name)
                    result = func(*args, **kwargs)
                except:
                    # the current timeout until the next try
                    current_timeout = timeout
                    # if it's set to incremental should be time * tries
                    if (incremental):
                        current_timeout = timeout * i
                    # log the error and sleep for the time accordingly
                    logger.error('Request failed (%s), retrying in %s...', func.func_name, current_timeout, exc_info=True)
                    sleep(current_timeout)
                    # keep on trying...
                    continue
                else:
                    # everything went fine return
                    return result
            else:
                # this is bad, log and raise
                logger.error('We`ve exhausted the number of retries, throwing the exception...', exc_info=True)
                raise NetworkError
        return inner
    return wrap
