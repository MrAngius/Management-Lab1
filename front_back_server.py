import complex_queued_web_service as cws
import random


class FrontEndServer(cws.ComplexQueue):
    def __init__(self, service_time, arrival_time, num_service, size, a, b, seed, environment, statistics,
                 back_end_queue, hit_cache=70):
        super(FrontEndServer, self).__init__(service_time, arrival_time, num_service, size, a, b, seed, environment,
                                             statistics)
        # i need to keep track of arrivals for the second queue, which are the end of service of the first for which
        # the content is not found in cache
        self.hit_percentage = hit_cache
        self.back_queue = back_end_queue

    def service(self):
        with self.services.request() as request:
            # this hold the request until the service is busy
            yield request

            # when the service is no more busy, we compute the service time
            service_time = random.expovariate(lambd=1.0 / self.service_time)

            # wait util the service won't finish
            yield self.env.timeout(service_time)

            # STATISTICS
            self.statistics.updateService(self.env.now)
            self.statistics.newServed()
            # update the customer average when a service has finished
            self.statistics.averageCustomersUpdate(self.env.now, len(self.services.queue))

            rand = random.uniform(0, 1) * 100

            if rand > self.hit_percentage:
                self.back_queue.arrivals()

    def arrivals(self):
        while True:
            # we compute the arrival time
            inter_arrival = random.expovariate(lambd=1.0 / self.arrival_time)

            # wait until a new packet arrives
            yield self.env.timeout(inter_arrival)

            if len(self.services.queue) < self.queue_size:

                # STATISTICS
                self.statistics.updateArrival(self.env.now)
                self.statistics.newArrival()
                # update the customer average when a new packet has arrived
                self.statistics.averageCustomersUpdate(self.env.now, len(self.services.queue))

                # call the service for a packet in the batch
                self.env.process(self.service())
            else:
                # increase the number of dropped packets by one
                self.statistics.updateDropped(1)


class BackEndServer(cws.ComplexQueue):
    def __init__(self, service_time, num_service, size, a, b, seed, environment, statistics):
        super(BackEndServer, self).__init__(service_time, None, num_service, size, a, b, seed, environment,
                                            statistics)

    def arrivals(self):
        # check if there's space in the queue
        if len(self.services.queue) < self.queue_size:

            # STATISTICS
            self.statistics.updateArrival(self.env.now)
            self.statistics.newArrival()
            # update the customer average when a new packet has arrived
            self.statistics.averageCustomersUpdate(self.env.now, len(self.services.queue))

            # call the service for a packet in the batch
            self.env.process(self.service())
        else:
            # increase the number of dropped packets by one
            self.statistics.updateDropped(1)
