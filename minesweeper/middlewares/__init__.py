from falcon import (
    HTTPError,
    HTTPInternalServerError
)

from .logging import LoggerMiddleware
from .require_json import RequireJSONMiddleware


def internal_error_handler(ex, req, resp, params):
    """Whenever an non-falcon exception is raised, it wraps it into a falcon.HTTPInternalServererror exception.

    :param ex: The exception caught
    :type ex: Exception
    :param req: The falcon request object
    :type req: falcon.Request
    :param resp: The falcon response object
    :type resp: falcon.Response
    :param params: Additional requests parameters
    :type params: dict
    """
    if not isinstance(ex, HTTPError):
        raise HTTPInternalServerError(description=repr(ex))
    else:
        raise ex
