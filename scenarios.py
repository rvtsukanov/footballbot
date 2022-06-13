from core import read_parameter

SESSION_ADMINS = read_parameter("admins")
SESSION_ONLY = lambda m: m.from_user.username in SESSION_ADMINS
GROUP_ONLY = lambda m: m.chat.type == "group"
ALWAYS_TRUE = lambda m: True