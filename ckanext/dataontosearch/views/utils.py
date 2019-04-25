import logging
import functools


logger = logging.getLogger(__name__)


def _log_exceptions(f):
    '''
    Log any exception that occurs while running the decorated function.
    '''
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            logger.exception(u'Exception occurred while processing route')
            raise
    return wrapper
