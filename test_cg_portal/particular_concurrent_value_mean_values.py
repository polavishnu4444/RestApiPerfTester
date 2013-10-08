from datetime import datetime
import random
import time
import gevent
from perf_measure import TestMeta
MEAN_TOTAL = 10

def start_perf_record():
    concurrency_classes =  [1, 2, 4, 5, 10, 20,40, 50, 100]
    random_file_number = random.randint(0, 12345678)
    filename = "app"+str(datetime.now().strftime("%m-%d-%y%H%M%S"))+".txt"
    f = open(filename, 'w')
    for con in concurrency_classes:
        ping = TestMeta()
        print "\n\n============== concurrency change to "+str(con)+"================="
        ping.CONCURRENCY = con
        ping.result = []
        counter = 1
        prev_len = 0
        ping.perfTester(counter)
        # gevent.joinall(ping.future)
        while counter != MEAN_TOTAL or len(ping.result) != MEAN_TOTAL:
            if counter != MEAN_TOTAL and prev_len <= len(ping.result):
                counter += 1
                gevent.sleep(1)
                ping.perfTester(counter)
                # gevent.joinall(ping.future)
                prev_len = len(ping.result)
            elif len(ping.result) != MEAN_TOTAL:
                continue
        print "===============condensed result==============="
        # ping.result[0] = (x for x in ping.result)
        print "{0},{1}".format(con, reduce(lambda x, y: x + y, ping.result) / len(ping.result))

        f.write("{0},{1}\n".format(con, reduce(lambda x, y: x + y, ping.result) / len(ping.result)))
        f.flush()
        print "\n\n"

if __name__ == "__main__":
    start_perf_record()

