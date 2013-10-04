import json
import requests
from lib.cloudgust.core.data_providers import CloudgustDataProvider
from lib.cloudgust.core.entity import CGObject, CGCollection
from lib.cloudgust.utils.Logger import CGLogger

CG_USER = 1
CG_APP_USER = 2

class CGAuthUserManger():
    def __init__(self):
        from django.conf import settings
        self.authServer = getattr(settings, 'APPSERVER_AUTHSERVER_URL', 'http://localhost:7890/')
        self.logger_object = CGLogger()
        self.logger = self.logger_object.get_logger('cg_auth_server_user_manager')


    def _authenticate_appuser_token(self, token):
        if not token:
            raise Exception("Invalid token")

        if token.startswith('"'):
            token = token[1:-1]

        url = self.authServer+"authenticateappuser"
        token = str(token)
        data = json.dumps({
            "token":token
        })
        self.logger.info("Sending token authenticate request to auth server", extra={"data_to_auth":data})
        try:
            r = requests.post(url, data);
            if r.status_code >=200 and r.status_code <= 299:
                res = r.json()
                self.logger.info("Authenticated with", extra={"auth_server_resp":str(res)})
                return {'userName':res['userName']}
            else:
                self.logger.warning("Auth server authenticate app user using token rejected",extra={"data_to_auth":data,
                                                                                                    "auth_server_resp":r.content})
                raise Exception(r.content)
        except Exception as e:
            self.logger.error("Error with authentication server:", extra={"data_to_auth":data, "Message":e.message})
            return e.message

    def _authenticate_cguser_token(self, token):
        if not token:
            self.logger.warning("invalid token. Token empty")
            raise Exception("Invalid token")

        url = self.authServer+"authenticatecguser"
        data = json.dumps({
            "token":token
        })
        self.logger.info("Sending cguser token authenticate request to auth server", extra={"data_to_auth":data})
        try:
            r = requests.post(url, data)
            r.raise_for_status()
            res = r.json()
            self.logger.info("Authenticated with", extra={"auth_server_resp":str(res)})
            return res['userName']
        except Exception as e:
            self.logger.error("Error with authentication server:", extra={"data_to_auth":data, "Message":e.args[0]})
            return None

    def _authenticate_cg_user(self, username, password):
        try:
            if not username:
                raise Exception("Invalid username")
            if not password:
                raise Exception("Invalid password")

            url = self.authServer+"authenticatecguser"
            data = json.dumps({
                "userName":username,
                "password":password
            })
            self.logger.info("Sending cguser cred authenticate request to auth server", extra={"data_to_auth":username})
            r = requests.post(url, data)
            if r.status_code >=200 and r.status_code <= 299:
                res = r.json()
                self.logger.info("Authenticated with", extra={"auth_server_resp":str(res)})
                return res['token']
            else:
                self.logger.warning("Authenticate user failed", extra={"data_to_auth":username, "auth_server_resp":str(r.content)})
                raise Exception(r.content)
        except Exception as e:
            self.logger.error("Error with authentication server:", extra={"data_to_auth":username, "Message":e.message})
            return

    def _activate_user(self, activation_code):
       url = self.authServer+"activatecguser"
       data = json.dumps({
           "activation_token":activation_code
       })
       self.logger.info("Sending activate cguser request to auth server", extra={"data_to_auth":data})
       r = requests.post(url, data);
       return r

    def _activate_app_user(self, activation_code):
       url = self.authServer+"activateappuser"
       data = json.dumps({
           "activation_token":activation_code
       })
       self.logger.info("Sending activate app user request to auth server", extra={"data_to_auth":data})
       r = requests.post(url, data)
       return r

    def _create_authentication_user(self,username, password):
        url = self.authServer+"signupcguser"
        data = json.dumps({
            "userName":username,
            "password":password
        })
        self.logger.info("Sending authenticate app user request to auth server", extra={"data_to_auth":username})
        r = requests.post(url, data)
        return r

    def _renew_user_token(self, token, api):
        if not token:
            raise Exception("Invalid Token")
        url = self.authServer+api
        data = json.dumps({
            "token":token
        })
        self.logger.info("Sending renew token request to auth server", extra={"data_to_auth":data})
        try:
            r = requests.post(url, data);
            r.raise_for_status()
            res = r.json()
            self.logger.info("Authenticated with", extra={"auth_server_resp":str(res)})
            return res['token']
        except Exception as e:
            self.logger.error("Error with authentication server:", extra={"data_to_auth":data, "Message":e.message})
            return

    def _get_app_user_forgot_password_token(self, username):
        url = self.authServer+"appuserforgotpassword"
        print url
        data = json.dumps({
            "userName":username
        })
        self.logger.info("Sending get token for forgot password request to auth server", extra={"data_to_auth":data})
        r = requests.post(url, data);
        return r
        pass

    def _get_user_authentication_token(self, username):
        url = self.authServer+"cguserforgotpassword"
        print url
        data = json.dumps({
            "userName":username
        })
        self.logger.info("Sending get token for forgot password request to auth server", extra={"data_to_auth":data})
        r = requests.post(url, data);
        return r
        pass

    def _validate_reset_token(self, token, api):
        url = self.authServer+api
        data = json.dumps({
            "reset_token":token
        })
        self.logger.info("Sending validate token request to auth server", extra={"data_to_auth":data})
        r = requests.post(url, data);
        return r
        pass

    def _reset_password_user(self, password, username, token, api):
        url = self.authServer+api
        data = json.dumps({
            "reset_token":token,
            "password":password,
            "userName":username
        })
        self.logger.info("Sending password reset request to auth server", extra={"data_to_auth":data})
        r = requests.post(url, data)
        return r
        pass

    #     --------------------------------------------------------App users and tenants Auth -------------------------------------------------

    def _create_app_user(self, clientId, tenantId, userName, password):
        print "user creation "
        url = self.authServer + "createuser"
        data = json.dumps({
            "clientId": clientId,
            "tenantId": tenantId,
            "userName": userName,
            "password": password
        })
        self.logger.info("Sending create app user request to auth server", extra={"data_to_auth":userName})
        r = requests.post(url, data)
        return r

    def _create_app_tenant(self, appid, tenantId):
        print "auth tenant creation"
        url = self.authServer + "createtenant"
        data = json.dumps({
            "clientId": appid,
            "tenantId": tenantId
        })
        self.logger.info("Sending create tenant request to auth server", extra={"data_to_auth":data})
        r = requests.post(url, data)
        return r

    def _activate_app_tenant(self, clientId, tenantId):
        print "tenant activation"
        url = self.authServer+ "activatetenant"
        data = json.dumps({
            "clientId":clientId,
            "tenantId":tenantId
        })
        self.logger.info("Sending activate tenant request to auth server", extra={"data_to_auth":data})
        r = requests.post(url, data)
        return r

    def _authetincate_app_user(self, userName, password, clientId, tenantId, clientKey):
        try:
            if not userName:
                self.logger.warning("Empty userName")
                raise Exception("Invalid username")
            if not clientId:
                self.logger.warning("Empty clientId")
                raise Exception("Invalid clientId")
            if not tenantId:
                self.logger.warning("Empty tenantId")
                raise Exception("Invalid tenantId")
            if not clientKey:
                self.logger.warning("Empty clientKey")
                raise Exception("Invalid clientKey")
            if not password:
                self.logger.warning("Empty password")
                raise Exception("Invalid password")

            url = self.authServer+"authenticateappuser"
            data = json.dumps({
                "userName":userName,
                "password":password,
                "clientId":clientId,
                "tenantId":tenantId,
                "clientKey":clientKey
            })
            self.logger.info("Sending authenticate app request to auth server", extra={"data_to_auth":userName})
            r = requests.post(url, data);
            # r.raise_for_status()
            if r.status_code >=200 and r.status_code <= 299:
                res = r.json()
                self.logger.info("Authenticated with", extra={"auth_server_resp":str(res)})
                return {'token':res['token']}
            else:
                raise Exception(r.content)
        except Exception as e:
            self.logger.error("Error with authentication server:", extra={"data_to_auth":userName, "Message":e.message})
            return e.message


class CGUserManager():
    def __init__(self):
        from django.conf import settings
        self.appServer = getattr(settings, 'APPSERVER_URL')
        self.authServer = getattr(settings, 'APPSERVER_AUTHSERVER_URL')
        self.appServerId = getattr(settings, 'APPSERVER_CLIENTID')
        self.appServerKey = getattr(settings, 'APPSERVER_CLIENTKEY')
        self.tenantId = getattr(settings, 'APPSERVER_TENANTID')
        self.userId = getattr(settings, 'APPSERVER_USERID')
        self.userKey = getattr(settings, 'APPSERVER_USERKEY')
        self.user_profiles_string = "UserProfiles"
        self.provider = CloudgustDataProvider(self.appServer, self.appServerId, self.appServerKey, self.tenantId, self.userId, self.userKey)
        self.authManager = CGAuthUserManger()
        self.logger_object = CGLogger()
        self.logger = self.logger_object.get_logger('cg_user_manager')

    def forgot_password_cg_user(self, userName):
        try:
            profile = self.get_cg_user_profile_by_username(userName)
            if not profile:
                self.logger.warning("no such user exists", extra={"userName":userName})
                raise Exception("No such user exists")
            # if not 'isActive' in profile:
            #     raise Exception("User not activated, re-sign up or activate to continue")
            token = self.authManager._get_user_authentication_token(userName)
            if token.status_code == 200:
                token = token.text
                self.logger.info("got the forgot pwd token", extra={"forgot_pwd_token":token})
                return token
            else:
                self.logger.warning("failed to get the token", extra={"userName":userName, "Message":token.text})
                raise Exception(token.text)
        except Exception as e:
            self.logger.error("Failed for password reset because", extra={"Message":e.args[0], "userName":userName})
            raise Exception("Failed for password reset because {0}".format(e.args[0]))

    def activate_cg_user(self, activation_code):
        response = self.authManager._activate_user(activation_code)

        if response.status_code == 200:
            profile = CGCollection(self.user_profiles_string);
            provider = CloudgustDataProvider(self.appServer, self.appServerId, self.appServerKey, self.tenantId, self.userId, self.userKey)
            print response.text
            profile.load(provider, {"userName":response.text})
            print profile
            if profile:
                if not profile.collection:
                    self.logger.warning("No user with user name", extra={"userName":response.text})
                    raise Exception("Invalid user")
                user = filter(lambda active_user: active_user.get('isDeleted') == False, profile.collection)
                self.logger.info("this is the profile needed", extra={"userData":str(user[0])})
                return user[0].to_dict()
            else:
                raise Exception("no user")
        else:
            raise Exception(response.text)

    def create_new_cg_user(self, user_data):
        try:
            print "Creating new user"
            username = user_data["userName"]
            password = user_data["password"]
            if not username:
                raise Exception("username not specified")
            if not password:
                raise Exception("password not specified")
            response = self.authManager._create_authentication_user(username, password)
            if response.status_code == 200:
                self._delete_user_name(username)
                self._create_new_user_profile(user_data)
                return response.text
            else:
                raise Exception(response.text)
        except Exception as e:
            print e
            raise Exception("Error in creating new user:{0}".format(e.args[0]))

    def _create_new_user_profile(self, user_data):
        profile = CGObject(self.user_profiles_string)

        for pair in user_data.iteritems():
            if(pair[0] == "password"):
                continue

            profile.set(pair[0], pair[1])

        profile.set("isDeleted", False)
        profile.save(self.provider)
        return profile.to_dict()

    def _delete_user_name(self, username):
        print "deleting user", username
        user = None
        try:
            user = self.get_cg_user_profile_by_username(username)
        except Exception as e:
            print e
        print "this is the user fetched", user
        profile = CGObject(self.user_profiles_string)
        if user:
            profile.set("id", user["id"])
            profile.delete(self.provider)

    def get_cg_user_profile_by_username(self, username):
        if not username:
            raise Exception("Invalid username")
        profiles = CGCollection(self.user_profiles_string);
        profiles.load(self.provider, query={'userName':username})
        print "\nProfiles count", len(profiles.collection)
        if not profiles.collection:
            print "No users with user name: ",username
            raise Exception("Invalid user")
        user = filter(lambda active_user: active_user.get('isDeleted') == False, profiles.collection)
        print "this is the user list", user
        return user[0].to_dict()

    def reset_cguser_password_validate_token(self, token):
        if not token:
            raise Exception("Invalid token")
        response = self.authManager._validate_reset_token(token, "validateresettoken")
        if response.status_code == 200:
            return response.text
        else:
            return {"error":response.text}
        # link to auth server to validate the token
        pass

    def reset_password_cguser(self, password, username, token):
        if not password:
            raise Exception("required field missing")
        if not username:
            raise Exception("required field missing")
        if not token:
            raise Exception("required field missing")

        response = self.authManager._reset_password_user(password, username, token, "resetpassword")
        if response.status_code == 200:
            return True
        else:
            return {"error": response.text}

    def authenticate_cg_user(self, userName, password):
        return self.authManager._authenticate_cg_user(userName, password)

    def authenticate_cguser_token(self, token):
        return self.authManager._authenticate_cguser_token(token)

    def renew_cguser_token(self, token):
        return self.authManager._renew_user_token(token, "renewcgusertoken")


class AppUserManager():
    def __init__(self):
        from django.conf import settings
        self.appServer = getattr(settings, 'APPSERVER_URL')
        self.authServer = getattr(settings, 'APPSERVER_AUTHSERVER_URL')
        self.appServerId = getattr(settings, 'APPSERVER_CLIENTID')
        self.appServerKey = getattr(settings, 'APPSERVER_CLIENTKEY')
        self.tenantId = getattr(settings, 'APPSERVER_TENANTID')
        self.userId = getattr(settings, 'APPSERVER_USERID')
        self.userKey = getattr(settings, 'APPSERVER_USERKEY')
        self.user_profiles_string = "UserProfiles"
        self.provider = CloudgustDataProvider(self.appServer, self.appServerId, self.appServerKey, self.tenantId, self.userId, self.userKey)
        self.cgUserManager = CGUserManager()
        self.authManager = CGAuthUserManger()
        self.app_user_profiles_string = "AppUserProfiles"
        self.tenant_profiles_string = "TenantProfiles"
        self.logger_object = CGLogger()
        self.logger = self.logger_object.get_logger('app_user_manager')


    def create_new_cg_app_tenant_profile(self, clientId, data):
        print "inside create new tenant"
        if not clientId:
            print "no app id"
            raise Exception("App id not specified")
        if "tenantName" not in data:
            print "no tenant name"
            raise Exception("required fields not mentioned")
        if not data["tenantName"]:
            print "no tenant name"
            raise Exception("Invalid tenant name or id")
        print "creating tenant profile"
        r = self.authManager._create_app_tenant(clientId, data["tenantName"])
        print r.status_code
        if r.status_code >= 200 and r.status_code <=299:
            profile = CGObject(self.tenant_profiles_string)

            for field in data:
                profile.set(field, data[field])

            profile.set("clientId", clientId)
            profile.save(self.provider)
            if not profile.get("id"):
                print "tenant profile creation error"
                raise Exception("Error in tenant creation")
            print "profile created", json.loads(profile.to_json())
            r = self.authManager._activate_app_tenant(clientId, data["tenantName"])
            if r.status_code >= 200 and r.status_code <=299:
                return json.loads(profile.to_json())
            else:
                profile.delete(self.provider)
        print r.content
        return r.content

    def create_new_cg_app_user(self, user_data):
        print "Creating new user"
        if "userName" not in user_data:
            raise Exception("Required field misssing")
        if "clientId" not in user_data:
            raise Exception("Required field missing")
        if "tenantId" not in user_data:
            raise Exception("Required field missing")
        if "password" not in user_data:
            raise Exception("Required field missing")

        username = user_data["userName"]
        clientId = user_data["clientId"]
        tenantId = user_data["tenantId"]
        password = user_data["password"]
        if not username:
            raise Exception("username not specified")
        if not clientId:
            raise Exception("client id not specified")
        if not tenantId:
            raise Exception("tenant id not specified")
        if not password:
            raise Exception("password not specified")

        r = self.authManager._create_app_user(clientId, tenantId, username, password)
        if r.status_code >= 200 and r.status_code <=299:
            self._delete_app_user(username)
            return self._create_app_user(clientId, tenantId, user_data, r.text)
        print r.content
        return r.content

    def _delete_app_user(self, userName):
        print "deleting user", userName
        user = None
        try:
            user = self.get_app_user_profile_by_username(userName)
        except Exception as e:
            print e
        print "this is the user fetched", user
        profile = CGObject(self.app_user_profiles_string)
        if user:
            profile.set("id", user["id"])
            profile.delete(self.provider)

    def get_app_user_profile_by_username(self, userName):
        if not userName:
            raise Exception("Invalid username")
        profiles = CGCollection(self.app_user_profiles_string);
        profiles.load(self.provider, query={'app_user_name':userName})
        print "\nProfiles count", len(profiles.collection)
        if not profiles.collection:
            print "No users with user name: ",userName
            raise Exception("Invalid user")
        user = filter(lambda active_user: active_user.get('isDeleted') == False, profiles.collection)
        print "this is the user list", user
        return user[0].to_dict()

    def _create_app_user(self, clientId, tenantId, user_data, code):
        profile = CGObject("%s" % self.app_user_profiles_string)
        # profile.set("app_user_name", user_name)
        # this is temporary, here using this id to fetch the name of the tenant.
        profile.set("tenantId", tenantId)
        profile.set("clientId", clientId)
        profile.set("isDeleted", False)

        for key in user_data:
            if key == "password":
                continue
            profile.set(key, user_data[key])

        profile.save(self.provider)
        if not profile.get("id"):
            print "usre profile creation error"
            raise Exception("Error in user creation")
        profile.set("activation_code", code)
        return json.loads(profile.to_json())

    def list_app_tenants(self, appid):
        if not appid:
            print "app id is not present"
            raise Exception("App id is not present")
        tenants = CGCollection("%s" % self.tenant_profiles_string)
        tenants.load(self.provider,{"clientId":appid})

        if (len(tenants.collection) == 0):
            return None
        tenants = json.loads(tenants.to_json())
        # tenants = [t.to_dict for t in tenants.collection]
        print "these are the tenants fetched",tenants
        return tenants

    def list_app_tenant_users(self, appid, tenantid):
        if not appid:
            print "app id is not present"
            raise Exception("App id not present")
        if not tenantid:
            print "tenant id is not present"
            raise Exception("Tenant id not present")
        users = CGCollection("%s" % self.app_user_profiles_string)
        users.load(self.provider, {"tenantId":tenantid, "clientId":appid})

        if (len(users.collection) == 0):
            return None
        print "test of json: ",users.to_json()
        users = json.loads(users.to_json())
        # users = [t.to_json for t in users.collection]
        print "these are the users fetched", users
        return users

    def activate_cg_app_user(self, activation_code):
        print "User activation started"

        response = self.authManager._activate_app_user(activation_code)

        if response.status_code == 200:
            profile = CGCollection(self.app_user_profiles_string)
            provider = CloudgustDataProvider(self.appServer, self.appServerId, self.appServerKey, self.tenantId, self.userId, self.userKey)
            print response.text
            profile.load(provider, {"userName":response.text})
            print profile
            if profile:
                if not profile.collection:
                    print "No users with user name: ", response.text
                    raise Exception("Invalid user")
                user = filter(lambda active_user: active_user.get('isDeleted') == False, profile.collection)
                print "this is the profile needed: ", str(user[0])
                return user[0].to_dict()
            else:
                raise Exception("no user")
        else:
            raise Exception(response.text)

    def forgot_password_app_user(self, userName):
        try:
            profile = self.get_app_user_profile_by_username(userName)
            print "Existing profile ", profile
            if not profile:
                raise Exception("No such user exists")
            # if not 'isActive' in profile:
            #     raise Exception("User not activated, re-sign up or activate to continue")
            token = self.authManager._get_app_user_forgot_password_token(userName)
            if token.status_code == 200:
                token = token.text
                print "got the user token ", token
                return token
            else:
                print token.text
                raise Exception(token.text)
        except Exception as e:
            print "This is the exception ", e
            raise Exception("Failed for password reset because {0}".format(e.args[0]))

    def reset_app_user_password_validate_token(self, token):
        if not token:
            raise Exception("Invalid token")
        response = self.authManager._validate_reset_token(token, "validateappuserresettoken")
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(response.text)
        # link to auth server to validate the token
        pass

    def reset_password_app_user(self, password, userName, token):
        if not password:
            raise Exception("required field missing")
        if not userName:
            raise Exception("required field missing")
        if not token:
            raise Exception("required field missing")

        response = self.authManager._reset_password_user(password, userName, token, "resetappuserpassword")
        if response.status_code == 200:
            return True
        else:
            response.raise_for_status()
            raise Exception(response.text)

    def authenticate_app_user(self, userName, password, clientId, tenantId, clientKey):
        return self.authManager._authetincate_app_user(userName, password, clientId, tenantId, clientKey)

    def authenticate_appuser_token(self, token):
        return self.authManager._authenticate_appuser_token(token)

    def renew_appuser_token(self, token):
        return self.authManager._renew_user_token(token,"renewappusertoken")


class UserManager():
    def __init__(self):
        from django.conf import settings
        self.appServer = getattr(settings, 'APPSERVER_URL', 'http://localhost:9998/1/')
        self.authServer = getattr(settings, 'APPSERVER_AUTHSERVER_URL', 'http://localhost:7890/')
        self.appServerId = getattr(settings, 'APPSERVER_CLIENTID', '523c676225da5f0a9447e84e')
        self.appServerKey = getattr(settings, 'APPSERVER_CLIENTKEY', 'key')
        self.tenantId = getattr(settings, 'APPSERVER_TENANTID', '1')
        self.userId = getattr(settings, 'APPSERVER_USERID', "admin")
        self.userKey = getattr(settings, 'APPSERVER_USERKEY', "admin")
        self.user_profiles_string = "UserProfiles"
        self.tenant_profiles_string = "TenantProfiles"
        self.app_user_profiles_string = "AppUserProfiles"
        self.provider = CloudgustDataProvider(self.appServer, self.appServerId, self.appServerKey, self.tenantId, self.userId, self.userKey)
        self.cgUserManager = CGUserManager()
        self.appUserManager = AppUserManager()

    def reset_password(self, type_of_user, password, username, token):
        if type_of_user == CG_USER:
            return self.cgUserManager.reset_password_cguser(password, username, token)
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.reset_password_app_user(password, username, token)

    def reset_password_validate_token(self, type_of_user, token):
        if type_of_user == CG_USER:
            return self.cgUserManager.reset_cguser_password_validate_token(token)
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.reset_app_user_password_validate_token(token)

    def forgot_password_user(self, type_of_user, userName):
        if type_of_user == CG_USER:
            return self.cgUserManager.forgot_password_cg_user(userName)
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.forgot_password_app_user(userName)

    def authenticate_token(self, type_of_user, token):
        if type_of_user == CG_USER:
            return self.cgUserManager.authenticate_cguser_token(token)
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.authenticate_appuser_token(token)

    def authenticate_user(self, type_of_user, userName, password, clientId=None, tenantId = None, clientKey = None):
        if type_of_user == CG_USER:
            return self.cgUserManager.authenticate_cg_user(userName, password)
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.authenticate_app_user(userName, password, clientId, tenantId, clientKey)

    def create_new_user(self, type_of_user, user_data):
        if type_of_user == CG_USER:
            return self.cgUserManager.create_new_cg_user(user_data)
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.create_new_cg_app_user(user_data)

    def activate_new_user(self, type_of_user, activation_code):
        if type_of_user == CG_USER:
            return self.cgUserManager.activate_cg_user(activation_code)
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.activate_cg_app_user(activation_code)

    def get_user_profile_by_username(self, type_of_user, userName):
        if type_of_user == CG_USER:
            return self.cgUserManager.get_cg_user_profile_by_username(userName)
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.get_app_user_profile_by_username(userName)

    def renew_token(self, type_of_user, token):
        if type_of_user == CG_USER:
            return self.cgUserManager.renew_cguser_token(token)
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.renew_appuser_token(token)

    def create_app_tenant(self, type_of_user, appid, user_data):
        if type_of_user == CG_USER:
            raise Exception("cannot create tenant for this type of user")
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.create_new_cg_app_tenant_profile(appid, user_data)

    def get_app_tenants(self, type_of_user, appid):
        if type_of_user == CG_USER:
            raise Exception("cannot create tenant for this type of user")
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.list_app_tenants(appid)

    def get_app_tenant_users(self, type_of_user, appid, tenantid):
        if type_of_user == CG_USER:
            raise Exception("cannot create tenant for this type of user")
        elif type_of_user == CG_APP_USER:
            return self.appUserManager.list_app_tenant_users(appid, tenantid)






