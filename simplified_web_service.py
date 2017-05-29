import simpy
import random


class Queue:
    def __init__(self, service_time, arrival_time, num_service, environment, service_stats, customer_stats):
        self.services = simpy.Resource(environment, num_service)
        self.server_number = num_service
        self.service_time = service_time
        self.arrival_time = arrival_time
        self.env = environment

        self.service_stats = service_stats
        self.customer_stats = customer_stats
        random.seed(random.randint(1, 10))

    def service(self, packet):
        with self.services.request() as request:
            # this hold the request until the service is busy
            yield request

            # when the service is no more busy, we compute the service time
            inter_service = random.expovariate(lambd=1.0 / self.service_time)

            # wait util the service won't finish
            yield self.env.timeout(inter_service)

            self.endService(inter_service, packet)

    def arrivals(self, packet=None):
        while True:
            # we compute the arrival time
            inter_arrival = random.expovariate(lambd=1.0 / self.arrival_time)

            # wait until a new packet arrives
            yield self.env.timeout(inter_arrival)

            self.callForService(inter_arrival, self.env.now)

    def callForService(self, inter_arrival, env_time):
        # STATISTICS
        packet = self.Packet()
        packet.addTimeArrival(env_time)
        packet.addComputedArrival(inter_arrival)

        # update the customer average when a new packet has arrived
        self.customer_stats.eventRegistration(env_time, len(self.services.queue))

        # call the service for a packet in the batch
        self.env.process(self.service(packet))

    def endService(self, inter_service, packet):
        # STATISTICS
        self.customer_stats.eventRegistration(self.env.now, len(self.services.queue))
        packet.addTimeService(self.env.now)
        packet.addComputedService(inter_service)

        # packet has been served, need to add it to the statistic's list
        self.service_stats.addPacket(packet)

    # inner class
    class Packet:
        def __init__(self):
            self.time_arrived = []
            self.time_served = []
            self.computed_arrivals = []
            self.computed_services = []
            self.dropped = False

        def addTimeArrival(self, time):
            self.time_arrived.append(time)

        def addTimeService(self, time):
            self.time_served.append(time)

        def addComputedArrival(self, inter_arrival):
            self.computed_arrivals.append(inter_arrival)

        def addComputedService(self, inter_service):
            self.computed_services.append(inter_service)

        def extractResponseTime(self):
            if not self.dropped:
                return [y - x for x, y in zip(self.time_arrived, self.time_served)]
