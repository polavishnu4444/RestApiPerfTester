import time
import gevent
from perf_measure import TestMeta
MEAN_TOTAL = 1


def start_perf_record():
    concurrency_classes =  [1, 2, 4, 5, 10, 20,40, 50, 100, 200, 400, 500, 1000]
    f = open("tmp2.txt","w")
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
                gevent.sleep(2)
                ping.perfTester(counter)
                # gevent.joinall(ping.future)
                prev_len = len(ping.result)
            elif len(ping.result) != MEAN_TOTAL:
                continue
        print "===============condensed result==============="
        print "{0},{1}".format(con,ping.result[0].total_seconds())

        f.write("{0},{1}\n".format(con,ping.result[0].total_seconds()))
        print "\n\n"

if __name__ == "__main__":
    start_perf_record()

