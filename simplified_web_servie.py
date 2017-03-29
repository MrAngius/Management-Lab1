import simpy
import random
from matplotlib import pyplot
import numpy


class Queue(object):
    def __init__(self, service_time, arrival_time, num_service, seed, environment, statistics):
        self.services = simpy.Resource(environment, num_service)
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

            # print "A packet has been served at time {}".format(self.env.now)
            self.stats.updateService((self.env.now, service_time))
            self.stats.newServed()

    def arrivals(self, queue):
        while True:
            # we compute the arrival time
            inter_arrival = random.expovariate(lambd=1.0 / self.arrival_time)

            # wait until a new packet arrives
            yield self.env.timeout(inter_arrival)

            # print "A packet arrived {}".format(self.env.now)
            self.stats.updateArrival((self.env.now, inter_arrival))
            self.stats.newArrival()

            # call the service for a packet
            self.env.process(queue.service())


class Statistics(object):
    def __init__(self):

        self.vector_arrival = []
        self.vector_service = []
        self.packet_arrived = 0
        self.packet_dropped = 0
        self.packet_served = 0

    def newArrival(self):
        self.packet_arrived += 1

    def newServed(self):
        self.packet_served += 1

    def newDropped(self):
        self.packet_dropped += 1

    def updateArrival(self, arrival_time):
        self.vector_arrival.append(arrival_time)

    def updateService(self, service_time):
        self.vector_service.append(service_time)

    def extractArrivals(self):
        arrival_intervals = []
        arrival_times = []
        for arrival in self.vector_arrival:
            arrival_times.append(arrival[0])
            arrival_intervals.append(arrival[1])
        return arrival_times, arrival_intervals

    def extractServices(self):
        service_intervals = []
        service_times = []
        for service in self.vector_service:
            service_times.append(service[0])
            service_intervals.append(service[1])
        return service_times, service_intervals

    def extractResponseTime(self):
        arrival_t = self.extractArrivals()[0]
        service_t = self.extractServices()[0]
        response_time = []
        for arr, ser in zip(arrival_t, service_t):
            response_time.append(ser - arr)
        return response_time


class Graphs(object):
    @staticmethod
    def printMeans(stats):
        print "Average inter-arrival time for packets: {}".format(numpy.mean(stats.extractArrivals()[1]))
        print "Average inter-service time for packets: {}".format(numpy.mean(stats.extractServices()[1]))
        print "Mean response time: {}".format(numpy.mean(stats.extractResponseTime()))

    # plot
    @staticmethod
    def plot_series(stats):
        fig, (series_arr, series_ser) = pyplot.subplots(2, 1)
        series_arr.plot(stats.extractArrivals()[1])
        series_arr.set_xlabel("Samples")
        series_arr.set_ylabel("Inter-arrival")
        series_ser.plot(stats.extractServices()[1])
        series_ser.set_xlabel("Samples")
        series_ser.set_ylabel("Inter-service")

    @staticmethod
    def plot_PDF(stats):
        fig2, (hist_arr, hist_ser) = pyplot.subplots(2, 1)
        hist_arr.hist(stats.extractArrivals()[1], bins=100, normed=True)
        hist_ser.hist(stats.extractServices()[1], bins=100, normed=True)

    @staticmethod
    def plot_CDF(stats):
        fig3, (cdf_arr, cdf_ser) = pyplot.subplots(2, 1)
        cdf_arr.hist(stats.extractArrivals()[1], bins=100, cumulative=True, normed=True)
        cdf_ser.hist(stats.extractServices()[1], bins=100, cumulative=True, normed=True)

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


if __name__ == '__main__':
    LAMBDA_ARRIVAL = 11
    MU_SERVICE = 8
    SIM_TIME = 100000
    RANDOM_SEED = 5
    SERVICE_NUMB = 1

    env = simpy.Environment()
    stats = Statistics()
    queue = Queue(MU_SERVICE, LAMBDA_ARRIVAL, SERVICE_NUMB, RANDOM_SEED, env, stats)
    env.process(queue.arrivals(queue))

    env.run(until=SIM_TIME)
    print "Arrived packets: {}".format(stats.packet_arrived)
    print "Packet served: {}".format(stats.packet_served)

    pyplot.close()
    Graphs.printMeans(stats)
    # Graphs.plot_series(stats)
    # Graphs.plot_PDF(stats)
    # Graphs.plot_CDF(stats)
    Graphs.plot_resp_time(stats)
    pyplot.show()
