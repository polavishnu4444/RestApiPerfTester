from UserManager import *


def test_signup_cg_user():
    from django.conf import settings
    settings.configure()
    userManager = UserManager()

    token = userManager.create_new_user(CG_USER,{
        "userName" : "polavishnu2@gmail.com",
        "password" : "123456"
    })
    if token:
        assert True
    else:
        assert False
    pass