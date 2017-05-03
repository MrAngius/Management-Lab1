import simpy
import random


class Queue(object):
    """class defining the model of a simple queue, providing arrivals and services"""

    def __init__(self, service_time, arrival_time, num_service, seed, environment, statistics):
        self.services = simpy.Resource(environment, num_service)
        self.server_number = num_service
        self.service_time = service_time
        self.arrival_time = arrival_time
        self.env = environment
        self.statistics = statistics
        random.seed(seed)

    def service(self):
        """service method describing the request of a service by a customer"""
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

    def arrivals(self):
        """arrival method describing the arrive of a customer"""
        while True:
            # we compute the arrival time
            inter_arrival = random.expovariate(lambd=1.0 / self.arrival_time)

            # wait until a new packet arrives
            yield self.env.timeout(inter_arrival)

            # STATISTICS
            self.statistics.updateArrival(self.env.now)
            self.statistics.newArrival()
            # update the customer average when a new packet has arrived
            self.statistics.averageCustomersUpdate(self.env.now, len(self.services.queue))

            # call the service for a packet
            self.env.process(self.service())


