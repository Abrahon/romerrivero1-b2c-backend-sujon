# accounts/utils.py
from accounts.models import B2BUser
from accounts.models import User as B2CUser

def is_b2b_user(user):
    return isinstance(user, B2BUser)

def is_b2c_user(user):
    return isinstance(user, B2CUser)
