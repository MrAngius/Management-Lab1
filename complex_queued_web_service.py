from simplified_web_service import Queue
import random


class ComplexQueue(Queue):

    def __init__(self, service_time, arrival_time, num_service, queue, seed, environment, statistics):
        super(ComplexQueue, self).__init__(service_time, arrival_time, num_service, seed, environment, statistics)
        self.queue_model = queue

    def arrivals(self, queue):
        while True:
            # we compute the arrival time
            inter_arrival = random.expovariate(lambd=1.0 / self.arrival_time)

            # wait until a new packet arrives
            yield self.env.timeout(inter_arrival)

            # print "A packet arrived {}".format(self.env.now)
            self.stats.updateArrival((self.env.now, inter_arrival))
            self.stats.newArrival()

            # create the batch

            # call the service for each batch
            # counter based on batch size


class QueueModel(object):

    def __init__(self, queue_size):
        self.queue_size = queue_size


class Batch(object):

    def __init__(self, a, b):
        self.batch_size = random.uniform(a, b)
