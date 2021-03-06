
# 3p
from bottle import response, request

# stdlib
import ddtrace
from ddtrace.ext import http


class TracePlugin(object):

    name = 'trace'
    api = 2

    def __init__(self, service="bottle", tracer=None):
        self.service = service
        self.tracer = tracer or ddtrace.tracer

    def apply(self, callback, route):

        def wrapped(*args, **kwargs):
            if not self.tracer or not self.tracer.enabled:
                return callback(*args, **kwargs)

            resource = "%s %s" % (request.method, request.route.rule)

            with self.tracer.trace("bottle.request", service=self.service, resource=resource) as s:
                code = 0
                try:
                    return callback(*args, **kwargs)
                except Exception:
                    # bottle doesn't always translate unhandled exceptions, so
                    # we mark it here.
                    code = 500
                    raise
                finally:
                    s.set_tag(http.STATUS_CODE, code or response.status_code)
                    s.set_tag(http.URL, request.path)
                    s.set_tag(http.METHOD, request.method)

        return wrapped


