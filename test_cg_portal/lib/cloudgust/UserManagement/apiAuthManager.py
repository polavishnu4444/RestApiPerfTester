from constants import *
from lib.cloudgust.utils.Logger import CGLogger

allowed_encrypted_users = []
allowed_ips = []
logger_object = CGLogger()
class AuthManager():
    def __init__(self):
        self.db = []
        self.logger_object = logger_object
        self.logger = self.logger_object.get_logger('api_auth_manager')

    def _decode_reset_token(self, message):
        # self.logger.warning("this is the encrypted user name: {0}".format(token[0]))
        # print "this is the message: ",message
        # message = triple_des(str(SHARED_KEY), CBC, pad=None, padmode=PAD_PKCS5).decrypt(str(message), padmode=2)
        # print "this is the message: ",message
        return message

    def is_authenticate_with_key(self, message, from_service_ip):
        self.logger.info("authenticating", extra={"service_message":message,"service_ip": from_service_ip})
        try:
            if not message in allowed_encrypted_users:
                requested_by = self._decode_reset_token(message)
                print requested_by, from_service_ip
                self.logger.info("requested by", extra={"service_message":requested_by})
                print "these are the allowed api users", allowed_api_users.values()
                if requested_by in allowed_api_users.values():
                     if from_service_ip in allowed_api_users.values():
                         allowed_encrypted_users.append(message)
                         allowed_ips.append(from_service_ip)
                         self.logger.info("allowed", extra={"service_message":message,"service_ip": from_service_ip})
                         return True
                self.logger.warning("not allowed", extra={"service_message":message,"service_ip": from_service_ip})
                return False
            else:
                if from_service_ip in allowed_ips:
                    self.logger.info("allowed", extra={"service_message":message,"service_ip": from_service_ip})
                    return True
                elif from_service_ip in allowed_api_users.values():
                    allowed_ips.append(from_service_ip)
                    self.logger.info("allowed", extra={"service_message":message,"service_ip": from_service_ip})
                    return True
            self.logger.warning("not allowed", extra={"service_message":message,"service_ip": from_service_ip})
            return False
        except Exception as e:
            print e
            self.logger.error("unknown error", extra={"service_message":message,
                                                      "service_ip": from_service_ip, "Message":e.message})
            return False