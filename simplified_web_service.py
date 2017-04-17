import simpy
import random
import simulation_p as simulation


class Queue(object):
    """class defining the model of a simple queue, providing arrivals and services"""

    def __init__(self, service_time, arrival_time, num_service, seed, environment, statistics):
        self.services = simpy.Resource(environment, num_service)
        self.server_number = num_service
        self.service_time = service_time
        self.arrival_time = arrival_time
        self.env = environment
        self.stats = statistics
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
            self.stats.updateService(self.env.now)
            self.stats.newServed()
            # update the customer average when a service has finished
            self.stats.averageCustomersUpdate(self.env.now, len(self.services.queue))

    def arrivals(self):
        """arrival method describing the arrive of a customer"""
        while True:
            # we compute the arrival time
            inter_arrival = random.expovariate(lambd=1.0 / self.arrival_time)

            # wait until a new packet arrives
            yield self.env.timeout(inter_arrival)

            # STATISTICS
            self.stats.updateArrival(self.env.now)
            self.stats.newArrival()
            # update the customer average when a new packet has arrived
            self.stats.averageCustomersUpdate(self.env.now, len(self.services.queue))

            # call the service for a packet
            self.env.process(self.service())


if __name__ == '__main__':
    LAMBDA_ARRIVAL = 10
    MU_SERVICE = 8
    SERVICE_NUMB = 1
    CONFIDENCE_INTERVAL = 0.95

    sim = simulation.SimulationRoh(LAMBDA_ARRIVAL, MU_SERVICE, SERVICE_NUMB, CONFIDENCE_INTERVAL)

    result = sim.confidenceIntervalResults(10, 0.2)

    print "Mean: {}".format(result["mean"])
    print "Interval: {}".format(result["interval"])

    # env = simpy.Environment()
    # stats = sc.Statistics()
    # queue = Queue(MU_SERVICE, LAMBDA_ARRIVAL, SERVICE_NUMB, RANDOM_SEED, env, stats)
    # env.process(queue.arrivals())
    # env.run(until=SIM_TIME)
    # print "Arrived packets: {}".format(stats.packet_arrived)
    # print "Packet served: {}".format(stats.packet_served)

    # pyplot.close()
    # Graphs.printMeans(stats)
    # Graphs.plot_resp_time(stats)
    # Graphs.plot_buffer_occupancy(stats)
    # pyplot.show()
