from datetime import datetime
import random
import time
from lib.cloudgust.core.data_providers import CloudgustDataProvider
from lib.cloudgust.core.entity import CGCollection, CGObject


def list_object(provider, className, counter, total_requests, total_failures):
    try:
        start_time = datetime.now()
        print "find", counter
        test_list = CGCollection(className)
        # test_list.load(provider, {"skip":100})
        total_requests +=1
        test_list.load(provider)
        print "found", len(test_list.collection)
        print "time for request",(datetime.now() - start_time)
        skip_count = 1
        # while len(test_list.collection) %100 == 0 and len(test_list.collection):
        #     test_list = CGCollection(className)
        #     total_requests +=1
        #     time.sleep(1)
        #     test_list.load(provider, {"skip":100*skip_count})
        #     skip_count += 1
        #     print "found", len(test_list.collection),skip_count
        print "\n"
        print "total REQUESTS of instance: ",total_requests
        print "total FAILURES of instance: ", total_failures
        print "\n\n"
        return (total_requests, total_failures)
    except Exception as e:
        total_failures += 1
        print e, total_failures
        print "\n"
        print "total REQUESTS of instance: ",total_requests
        print "total FAILURES of instance: ", total_failures
        print "\n\n"
        return (total_requests, total_failures)
    # print json.loads(test_list.to_json())


def save_object(provider, className, counter, total_requests, total_failures):
    try:
        start_time = datetime.now()
        print "save",counter
        save_obj = CGObject(className)
        save_obj.set("key"+str(counter), "value"+str(counter))
        total_requests += 1
        save_obj.save(provider)
        print "time for request",(datetime.now() - start_time)
        # time.sleep(1)
        print "saved object"
        print "\n"
        print "total REQUESTS of instance: ",total_requests
        print "total FAILURES of instance: ", total_failures
        print "\n\n"
        return (total_requests, total_failures)
    except Exception as e:
        total_failures += 1
        print e, total_failures
        print "\n"
        print "total REQUESTS of instance: ",total_requests
        print "total FAILURES of instance: ", total_failures
        print "\n\n"
        return (total_requests, total_failures)


def start_pinger(server):
    total_requests = 0
    total_failures = 0
    try:
        counter = 0
        while True:

            dataprovider = CloudgustDataProvider(server, "524e610a98c8efe25c000004",
                                         "2e2b3174-90e8-483e-a634-9b174c2e2f54", "1", "admin", "admin")
            call_func_decider = random.randint(0,1)
            if call_func_decider:
                total_requests, total_failures = list_object(dataprovider, "TempObject", counter, total_requests, total_failures)
            else:
                total_requests, total_failures = save_object(dataprovider, "TempObject", counter, total_requests, total_failures)
            # time.sleep(1)
            counter += 1

            dataprovider = CloudgustDataProvider(server, "524e610a98c8efe25c000004",
                                         "2e2b3174-90e8-483e-a634-9b174c2e2f54", "1", "vishnu", "vishnu")

            call_func_decider = random.randint(0,1)
            if call_func_decider:
                total_requests, total_failures = list_object(dataprovider, "TempObject", counter, total_requests, total_failures)
            else:
                total_requests, total_failures = save_object(dataprovider, "TempObject", counter, total_requests, total_failures)
            # time.sleep(1)
            counter += 1

            dataprovider = CloudgustDataProvider(server, "524e610a98c8efe25c000004",
                                         "2e2b3174-90e8-483e-a634-9b174c2e2f54", "1", "madhav", "madhav")

            call_func_decider = random.randint(0,1)
            if call_func_decider:
                total_requests, total_failures = list_object(dataprovider, "TempObject", counter, total_requests, total_failures)
            else:
                total_requests, total_failures = save_object(dataprovider, "TempObject", counter, total_requests, total_failures)
            # time.sleep(1)
            counter += 1



    except Exception as e:
        print e


if __name__ == "__main__":
    server = "http://ec2-46-137-227-13.ap-southeast-1.compute.amazonaws.com/1/"
    # server = "http://192.168.40.155:9997/1/"

    dataprovider = CloudgustDataProvider(server, "524bb2cd40dba1ec6a00003c",
                                         "2324f418-07a9-43fc-a496-e42bba6c9875", "1", "admin", "admin")

    dataprovider = CloudgustDataProvider(server, "524ad1d6b88d302846000030",
                                         "f01224dc-5d6a-45b5-a9be-6108241ee718", "1", "admin", "admin")

    start_pinger(server)
