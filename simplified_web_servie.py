import simpy
import random
from matplotlib import pyplot
import numpy
import statistic_collector as sc


class Queue(object):
    def __init__(self, service_time, arrival_time, num_service, seed, environment, statistics):
        self.services = simpy.Resource(environment, num_service)
        self.server_number = num_service
        self.service_time = service_time
        self.arrival_time = arrival_time
        self.env = environment
        self.stats = statistics
        random.seed(seed)

    def service(self):
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


class Graphs(object):
    @staticmethod
    def printMeans(stats):
        print "Average response time: {}\n".format(stats.computeAverageResponseTime())
        print "Average number of customers: {}\n".format(stats.computeAverageCustomers())

    @staticmethod
    def plot_resp_time(stats):
        pyplot.figure(1)

        # values
        pyplot.subplot(311)
        pyplot.plot(stats.extractResponseTime())
        pyplot.xlabel('i-th Packet')
        pyplot.ylabel('Response Time')
        pyplot.title('Packet Response Time')
        pyplot.grid(True)
        # pyplot.text(60, .025, r'$\mu=100,\ \sigma=15$')
        # pyplot.axis([40, 160, 0, 0.03])
        # pyplot.grid(True)

        # PDF
        pyplot.subplot(312)
        pyplot.hist(stats.extractResponseTime(), bins=100, normed=False)
        pyplot.xlabel('Response Time')
        pyplot.ylabel('Number of Packets')
        pyplot.title('PDF of Response Time')
        pyplot.grid(True)

        # CDF
        pyplot.subplot(313)
        pyplot.hist(stats.extractResponseTime(), bins=100, cumulative=True, normed=True)
        pyplot.xlabel('Response Time')
        pyplot.ylabel('Number of Packets')
        pyplot.title('CDF of Response Time')
        pyplot.grid(True)

    @staticmethod
    def plot_buffer_occupancy(stats):
        pyplot.figure(2)

        # buffer series
        pyplot.plot(stats.extractCustomerQueue())
        pyplot.xlabel('Samples')
        pyplot.ylabel('Number of Packets')
        pyplot.title('Trading of Buffer Occupancy')
        pyplot.grid(True)

if __name__ == '__main__':
    LAMBDA_ARRIVAL = 10
    MU_SERVICE = 8
    SIM_TIME = 1000000
    RANDOM_SEED = 5
    SERVICE_NUMB = 1

    env = simpy.Environment()
    stats = sc.Statistics()
    queue = Queue(MU_SERVICE, LAMBDA_ARRIVAL, SERVICE_NUMB, RANDOM_SEED, env, stats)
    env.process(queue.arrivals())
    env.run(until=SIM_TIME)
    print "Arrived packets: {}".format(stats.packet_arrived)
    print "Packet served: {}".format(stats.packet_served)

    #pyplot.close()
    Graphs.printMeans(stats)
    Graphs.plot_resp_time(stats)
    Graphs.plot_buffer_occupancy(stats)
    pyplot.show()
