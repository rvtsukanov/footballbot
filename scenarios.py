from core import read_parameter


class MessageScenario:
    """
    Class, overloading conditions as operators for message handlers only
    """
    def __init__(self, function):
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)

    def __and__(self, other):
        return MessageScenario(lambda m: self.function(m) and other.function(m))

    def __or__(self, other):
        return MessageScenario(lambda m: self.function(m) or other.function(m))


SESSION_ADMINS = read_parameter("admins")
ADMINS_ONLY = MessageScenario(lambda m: m.from_user.username in SESSION_ADMINS)
GROUP_ONLY = MessageScenario(lambda m: m.chat.type == "group")
PRIVATE_ONLY = MessageScenario(lambda m: m.chat.type == "private")
ALWAYS_TRUE = MessageScenario(lambda m: True)

QUERY_EXISTS = MessageScenario(lambda q: len(q.query) > 0)
QUERY_DEFAULT = MessageScenario(lambda q: len(q.query) > 0)
