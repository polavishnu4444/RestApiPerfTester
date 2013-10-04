import sys
#todo : WHat !! still using urllib2 !! move to requests
import urllib2
import urllib
from lib.cloudgust.utils.Logger import CGLogger
import json
from base64 import b64encode
from copy import deepcopy
from entity import CGObject 
import requests


class DataProvider:
    def get_by_id(entity_name,id):
        raise NotImplementedError()

    def get_all(entity_name,query):
        raise NotImplementedError()

    def save(entity_name, value):
        raise NotImplementedError()
    

class RestApiProvider:
    def __init__(self, host_url):
        self.host_url = host_url
        self.logger_object = CGLogger()
        self.logger = self.logger_object.get_logger('core_lib_rest')


    def get_headers(self, credentials):
        headers = {'content-type': 'application/json'}
        if(credentials):
           self.logger.info("Using Credentials", extra=credentials)
           headers['CG-CLIENTID'] = credentials['CLIENTID']
           headers['CG-CLIENTKEY'] = credentials['CLIENTKEY']
           headers['CG-TENANTID'] = credentials['TENANTID']
           headers['CG-USERID'] = credentials['USERID']
           headers['CG-USERKEY'] = credentials['USERKEY']
        return headers

    def get(self,relative_path, query=None, credentials=None):  
        entityUrl = self.host_url + relative_path
        self.logger.info("entity URL is:", extra={"entity_url":entityUrl})
        if(query):
            encoded_query = urllib.urlencode(query)
            entityUrl = entityUrl+"?"+encoded_query
            self.logger.info("entity URL is:", extra={"entity_url":entityUrl})
            # print "entityUrl is ",entityUrl

        headers = self.get_headers(credentials)
        # print headers
        response = requests.get(entityUrl, headers=headers)
        if response.status_code > 299:
            print response.content
        response.raise_for_status()
        data = response.json()
        self.logger.info("this is the data for the url", extra={"entity_url":entityUrl, "data_url":str(data)})
        # print "this is the data: {0} for the url: {1}".format(data,entityUrl)
        return data

    def post(self,relative_path, data, credentials=None):  
        entityUrl = self.host_url + relative_path
        self.logger.info("entity URL is:", extra={"entity_url":entityUrl})
        headers = self.get_headers(credentials)
        
        try:
            response = requests.post(entityUrl,data=data.to_json(), headers=headers)
            if response.status_code > 299:
                print response.content
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            print e
            self.logger.error("Unexpected error: ", extra={"Message":e.message})
            # print "Unexpected error:", e
            raise

    def put(self,relative_path, data, credentials=None):  
        entityUrl = self.host_url + relative_path
        self.logger.info("entity URL is:", extra={"entity_url":entityUrl})
        headers = self.get_headers(credentials)

        req = urllib2.Request(entityUrl,data=data.to_json(), headers=headers)
        try:
            response = requests.put(entityUrl,data=data.to_json(), headers=headers)
            
            data = response.json()
            return data
        except urllib2.HTTPError as e:
            self.logger.error("Unexpected error: ", extra={"Message":e.message})
            raise

    def delete(self, relative_path, credentials=None):
        entityUrl = self.host_url +relative_path
        self.logger.info("entity URL is:", extra={"entity_url":entityUrl})
        headers = self.get_headers(credentials)

        try:
            resp = requests.delete(entityUrl, headers=headers)
            # print "this is the response",resp
            data = resp.json()
            return data
        except urllib2.HTTPError as e:
            self.logger.error("Unexpected error: ", extra={"Message":e.message})
            raise


class CloudgustDataProvider(DataProvider):

    def __init__(self, serverUrl, appid, appkey, tenantId, userId, userKey):
        self.host_url = serverUrl
        #self.host_url = "http://www.bizkinetic.com"
        self.api_url = "api/"
        self.credentials = {
            "CLIENTID":appid,
            'CLIENTKEY':appkey,
            'TENANTID':tenantId,
            'USERID':userId,
            'USERKEY':userKey
        }
        self.api_provider = RestApiProvider(self.host_url+self.api_url)


    def get(self,entity_class, query=None): 
        data = self.api_provider.get(entity_class, query, self.credentials)
        return data
    
        
    def get_all(self,entity_class,query):
        return self.get(entity_class)

    def get_by_id(self,entity_class,id):
        url = self.get_entity_url(entity_class, id)
        return self.get(url)
        
    def save(self, entity):        
        id = entity.getid()        
        url = self.get_entity_url(entity.classname, id)

        if(id):
            print "check 1"            
            data = self.api_provider.put(url, entity ,self.credentials)
        else:
            print "check 2"
            data = self.api_provider.post(url, entity ,self.credentials)

        return data

    def get_entity_url(self, entity_class, id=None):        
        if(id):
            return "{0}/{1}".format(entity_class, id)
        else:
            return entity_class

    def get_entity_collection_url(self, entity_class, query):
        return

    def delete(self, entity_class, id):
        url = self.get_entity_url(entity_class, id)
        data = self.api_provider.delete(url, self.credentials)
        return data

    @classmethod
    def create(cls,context):
        return BizKineticDataProvider()


