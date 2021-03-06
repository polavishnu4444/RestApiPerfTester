from datetime import datetime
import json
import requests
# from requests_futures.sessions import FuturesSession
from lib.cloudgust.utils.Logger import CGLogger
import time
import gevent.monkey
gevent.monkey.patch_all()
logger_object = CGLogger()


class TestMeta:
    def __init__(self):
        self.CONCURRENCY = 0
        self.gr = requests
        self.response_count = 0
        self.start_time = None
        self.result = []
        self.logger = logger_object.get_logger('PerfMeasurer')
        self.fail_count = 0
        self.setNum = 0

    def bg_cb(self, resp, **kwargs):
        self.response_count += 1
        # print "got response", self.response_count
        # print resp
        # print resp.content
        if resp.status_code > 299:
            # print "failing", resp.content
            self.fail_count += 1

        # print fail_count

        # print len(resp.content)
        if self.response_count % self.CONCURRENCY == 0:
            diff = (datetime.now() - self.start_time)
            print "response total time:", diff
            print "failed:", self.fail_count
            self.result.append(diff)
            self.logger.info("data", extra={"requestNumber": self.setNum, "diffTime": str(diff),
                                          "concurrency": self.CONCURRENCY, "failCount": self.fail_count})
        # parse the json storing the result on the response object
        # resp.data = resp.json()

    def appServer(self):
        self.gr.get('http://ec2-46-137-227-13.ap-southeast-1.compute.amazonaws.com/1/api/NewTempObject',
                                      headers={"CG-CLIENTID": "5252b9b3a2fbcbc83a00002c",
                "CG-CLIENTKEY": "b4808c69-36ed-429f-8ca3-19df7227a35d",
                "CG-TENANTID": "1",
                "CG-USERID": "admin",
                "CG-USERKEY": "admin"}, hooks=dict(response=self.bg_cb))

    def appServerProd(self):
        self.gr.get('http://ec2-46-137-228-225.ap-southeast-1.compute.amazonaws.com/1/api/NewTempObject',
                                      headers={"CG-CLIENTID": "52536ca196fa6d171a000004",
                "CG-CLIENTKEY": "2df74b80-2d70-4a57-ab1c-5644f82bde31",
                "CG-TENANTID": "1",
                "CG-USERID": "admin",
                "CG-USERTOKEN":"82884d183b8d3d3fce1697fc0398c64c",
                "CG-USERKEY": "admin"}, hooks=dict(response=self.bg_cb))

    def authServer(self):
        self.gr.post('http://ec2-54-251-87-255.ap-southeast-1.compute.amazonaws.com:7890/authenticateappuser',
                                       data = json.dumps({"userName": "vishnu", "password":"vishnu", "clientId":"524e610a98c8efe25c000004",
                                                          "clientKey":"2e2b3174-90e8-483e-a634-9b174c2e2f54", "tenantId":"1"
                                                          }),
                                       hooks=dict(response=self.bg_cb))

    def authServerToken(self):
        self.gr.post('http://ec2-54-251-87-255.ap-southeast-1.compute.amazonaws.com:7890/authenticateappuser',
                                       data = json.dumps({"token":"1d15540ba5f93e5331b079ff8d6721c1"}),
                                       hooks=dict(response=self.bg_cb))

    def perfTester(self, setNumber):        
        self.setNum = setNumber
        counter = 1
        self.future = []
        self.start_time = datetime.now()
        sleep_time = float(1)/self.CONCURRENCY
        while counter <= self.CONCURRENCY:
            # print "requsted", counter
            counter += 1
            # self.future.append(gevent.spawn(self.authServer))
            self.future.append(gevent.spawn(self.appServer))
            # gevent.sleep(0)
            #gevent.sleep(sleep_time)
        # grequests.map(future)
        print "requested set", setNumber
        # print future
        print "sent", (datetime.now() - self.start_time)
        gevent.joinall(self.future)

# perfTester(5)


