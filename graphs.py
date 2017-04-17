from matplotlib import pyplot
import statistic_collector as sc


class Graphs(object):
    @staticmethod
    def printMeans(statistics):
        warm_up = sc.WarmUpCut(0.01)

        print "Average response time: {}\n".format(
            warm_up.eliminateWarmUpResponseTime(statistics.extractResponseTime()))
        print "Average number of customers: {}\n".format(statistics.computeAverageCustomers())

    @staticmethod
    def plot_resp_time(statistics):
        pyplot.figure(1)

        # values
        pyplot.subplot(311)
        pyplot.plot(statistics.extractResponseTime())
        pyplot.xlabel('i-th Packet')
        pyplot.ylabel('Response Time')
        pyplot.title('Packet Response Time')
        pyplot.grid(True)
        # pyplot.text(60, .025, r'$\mu=100,\ \sigma=15$')
        # pyplot.axis([40, 160, 0, 0.03])
        # pyplot.grid(True)

        # PDF
        pyplot.subplot(312)
        pyplot.hist(statistics.extractResponseTime(), bins=100, normed=False)
        pyplot.xlabel('Response Time')
        pyplot.ylabel('Number of Packets')
        pyplot.title('PDF of Response Time')
        pyplot.grid(True)

        # CDF
        pyplot.subplot(313)
        pyplot.hist(statistics.extractResponseTime(), bins=100, cumulative=True, normed=True)
        pyplot.xlabel('Response Time')
        pyplot.ylabel('Number of Packets')
        pyplot.title('CDF of Response Time')
        pyplot.grid(True)

    @staticmethod
    def plot_buffer_occupancy(statistics):
        pyplot.figure(2)

        # buffer series
        pyplot.plot(statistics.extractCustomerQueue())
        pyplot.xlabel('Samples')
        pyplot.ylabel('Number of Packets')
        pyplot.title('Trading of Buffer Occupancy')
        pyplot.grid(True)
