# utils/user_context.py
from contextvars import ContextVar
from typing import Optional, Dict

_user_context: ContextVar[Optional[Dict]] = ContextVar("_user_context", default=None)

def set_current_user(user: Dict):
    _user_context.set(user)

def get_current_user() -> Optional[Dict]:
    return _user_context.get()