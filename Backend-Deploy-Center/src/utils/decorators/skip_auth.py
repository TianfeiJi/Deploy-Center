# utils/decorators.py

def skip_auth(func):
    setattr(func, "_skip_auth", True)
    return func
