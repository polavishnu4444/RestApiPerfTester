from django.conf import settings
import socket

portal_server = socket.gethostbyname(getattr(settings,"PORTAL_IP"))
print "hello this is the portal server",portal_server
app_server = socket.gethostbyname(getattr(settings, "APPSERVER_IP"))
config_server = socket.gethostbyname(getattr(settings, "CONFIG_SERVER_IP"))
SHARED_KEY = "CG_SHARED_KEY_CG" #this is the shared key between services. This should be minimum 16 bytes

allowed_api_users = {
    "PORTAL_SERVER_NAME" : "cg_portal_server", #this is the one which tells that it is actually portal server
    "PORTAL_SERVER_IP" : portal_server,
    "APP_SERVER_IP" : app_server,
    "CONFIG_SERVER_IP":config_server,
    "CG_APP_SERVER":"cg_app_server"
}