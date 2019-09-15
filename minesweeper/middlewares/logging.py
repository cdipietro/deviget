import time
import uuid
from math import ceil

import falcon
from falcon.request import Request as FalconRequest
from falcon.response import Response as FalconResponse

from minesweeper.common.logging import get_app_logger


class LoggerMiddleware(object):
    """Middleware class that adds a log entry each time a new request is received and once it has already been
    processed.
    """

    def process_request(self, req, resp):
        """Assigns a request id to each new request received by the API.
        """
        new_id = uuid.uuid1().hex
        req.context['id'] = resp.context['id'] = new_id
        req.context['repr'] = resp.context['repr'] = f"{new_id}"
        req.context['req_start_time'] = time.time()

    def process_resource(self, req, resp, resource, params):
        """Adds a log entry to indicate the request began to be processed.
        """
        logger = get_app_logger()
        msg = [f"{req.method} {req.relative_uri}"]
        msg.append(f"headers = {req.headers}")
        if req.method in ('POST', 'PUT', 'PATCH'):
            msg.append(f'payload = {req.media}')
        logger.info(f"{req.context['repr']} :: Got request >> {' | '.join(msg)}")
        logger.debug(f"{req.context['repr']} :: Started processing")

    def process_response(self, req, resp, resource, req_succeeded):
        """Adds a log entry to indicate the request has finished being processed along with the time it took.
        """
        logger = get_app_logger()
        total_time = ceil((time.time() - req.context['req_start_time']) * 1000)
        msg = f'{resp.status} ({total_time} ms) | headers = {resp._headers}'
        if resp.data:
            msg += f' | payload = {resp.data.decode()}'
        elif resp.body:
            msg += f' | payload = {resp.body}'
        logger.debug(f"{resp.context['repr']} :: Finished processing")
        logger.info(f"{resp.context['repr']} :: Sent response >> {msg}")
