import falcon


class RequireJSONMiddleware(object):
    """Middleware class that checks for 'application/json' media-type required headers in
    API requests.
    """

    def process_request(self, req, resp):
        if not req.client_accepts_json:
            raise falcon.HTTPNotAcceptable('This API only supports responses encoded as JSON.')

        if req.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
            if not req.content_type or 'application/json' not in req.content_type:
                raise falcon.HTTPUnsupportedMediaType('This API only supports requests encoded as JSON.')
