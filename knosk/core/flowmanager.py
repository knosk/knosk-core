import logging

LOG = logging.getLogger(__name__)


def default_fallback(ex, route_name, payload, ctx):
    LOG.error(
        "Error %s occur while handling route %s with payload %s and ctx %s" %
        (ex, route_name, payload, ctx))
    LOG.exception(ex)
    raise ex


class SingleBotFlowFactory:
    _botflow = None

    @classmethod
    def get(cls, fallback):
        if cls._botflow:
            return cls._botflow
        else:
            cls._botflow = Flow(fallback)
            return cls._botflow


class Flow(object):

    def __init__(self, fallback=None):
        self.__handlers = {}
        self.__renders = {}
        self.__fallback = fallback if fallback else default_fallback

    def __route(self, route_name, location, payload=None, ctx=None):
        payload = payload if payload else {}
        ctx = ctx if ctx else {}
        try:
            if route_name in location:
                action = location[route_name]['action']
                conditions = location[route_name]['conditions']

                for condition in conditions:
                    result = condition(self, route_name, payload, ctx)
                    if result:
                        return result

                return action(self, route_name, payload, ctx)
            raise ValueError("Can't find route: %s" % route_name)
        except Exception as ex:
            return self.__fallback(ex, route_name, payload, ctx)

    def handle(self, route_name, payload=None, ctx=None):
        return self.__route(route_name, self.__handlers, payload, ctx)

    def render(self, route_name, payload=None, ctx=None):
        return self.__route(route_name, self.__renders, payload, ctx)

    def __register(self, route_name, location, conditions: list = []):
        def decorator(func):
            location[route_name] = {'action': func, 'conditions': conditions}
            return func

        return decorator

    def handler(self, route_name, conditions: list = []):
        return self.__register(route_name, self.__handlers, conditions)

    def renderer(self, route_name, conditions: list = []):
        return self.__register(route_name, self.__renders, conditions)

    def handler_names(self):
        return list(self.__handlers.keys())
