import simpy
import numpy
from scipy.stats import t
from complex_queued_web_service import ComplexQueue
from statistic_collector import Statistics
from simulation_p_1a import averageCustomers
from graphs import Graphs
from matplotlib import pyplot


class SimulationRohComplex(object):
    def __init__(self, lambda_arrival, mu_service, numb_services, confidence_interval, size, a, b, warm_up=False):

        self.lambda_arrival = lambda_arrival
        self.mu_service = mu_service
        self.numb_services = numb_services
        self.conf_interval = confidence_interval
        self.warm_up = warm_up
        self.size = size
        self.a = a
        self.b = b

    def runSim(self, long_sim=False):

        if long_sim:
            sim_time = 10000 * 10
        else:
            sim_time = 10000

        rand_seed = 50
        env = simpy.Environment()
        stats = Statistics()

        queue = ComplexQueue(self.mu_service, self.lambda_arrival, self.numb_services, self.size,
                             self.a, self.b, rand_seed, env, stats)
        env.process(queue.arrivals())
        env.run(until=sim_time)

        return stats

    def confidenceIntervalResults(self, numb_batches, p=0.2, dynamic_batch=False):
        """compute the student's t confidence interval and iterate increasing the batches if the interval is wide"""
        n = numb_batches
        z_resp = 100
        z_custom = 100
        z_drop = 100
        interval_resp = []
        interval_custom = []
        interval_drop = []
        mean_resp = 100.0
        mean_custom = 100.0
        mean_drop = 100.0

        stats = self.runSim(long_sim=True)

        # implementing the batch number computing the confidence interval on-the-fly
        while (2 * z_resp / mean_resp) > p and (2 * z_custom / mean_custom) and (2 * z_drop / mean_drop) > p:

            batches_response = stats.batchesResponseTime(n, True)
            batches_customers = stats.batchesCustomerQueue(n)
            batches_dropped = stats.batchesDroppedPackets(n)

            batches_response_means = [numpy.mean(batch) for batch in batches_response]
            batches_customers_means = [averageCustomers(batch) for batch in batches_customers]
            batches_dropped_means = [numpy.mean(batch) for batch in batches_dropped]

            mean_resp = numpy.mean(batches_response_means)
            mean_custom = numpy.mean(batches_customers_means)
            mean_drop = numpy.mean(batches_dropped_means)

            std_custom = numpy.std(batches_customers_means)
            std_resp = numpy.std(batches_response_means)
            std_drop = numpy.std(batches_dropped_means)

            interval_resp = t.interval(self.conf_interval, n, loc=mean_resp, scale=std_resp)
            interval_custom = t.interval(self.conf_interval, n, loc=mean_custom, scale=std_custom)
            interval_drop = t.interval(self.conf_interval, n, loc=mean_drop, scale=std_drop)

            z_resp = interval_resp[1] - mean_resp
            z_custom = interval_custom[1] - mean_custom
            z_drop = interval_drop[1] - mean_drop

            # ____debug____
            print n
            print std_resp, std_custom

            n += 1

            if not dynamic_batch:
                return {"mean_resp": mean_resp, "interval_resp": interval_resp,
                        "mean_custom": mean_custom, "interval_custom": interval_custom,
                        "mean_dropped": mean_drop, "interval_dropped": interval_drop}

        return {"mean_resp": mean_resp, "interval_resp": interval_resp,
                "mean_custom": mean_custom, "interval_custom": interval_custom,
                "mean_dropped": mean_drop, "interval_dropped": interval_drop}


if __name__ == '__main__':
    LAMBDA_ARRIVAL = 60.0
    MU_SERVICE = 8.0
    SERVICE_NUMB = 1
    CONFIDENCE_INTERVAL = 0.95
    SIZE = 50
    A = 3
    B = 5

    # vectors for collecting data
    means_resp = []
    means_custom = []
    means_dropped = []
    upper_interval_resp = []
    lower_interval_resp = []
    upper_interval_custom = []
    lower_interval_custom = []
    upper_interval_dropped = []
    lower_interval_dropped = []

    lambda_arr_values = []
    roh = []
    lambda_arr = LAMBDA_ARRIVAL

    # creation of the roh array
    while lambda_arr > MU_SERVICE:
        lambda_arr_values.append(lambda_arr)
        roh.append(MU_SERVICE / lambda_arr)
        lambda_arr -= .5

    for lambda_arr in lambda_arr_values:
        sim = SimulationRohComplex(lambda_arr, MU_SERVICE, SERVICE_NUMB, CONFIDENCE_INTERVAL, SIZE, A, B)
        temp = sim.confidenceIntervalResults(25)

        # saving the data in separate lists
        means_resp.append(temp["mean_resp"])
        means_custom.append(temp["mean_custom"])
        means_dropped.append(temp["mean_dropped"])
        upper_interval_resp.append(temp["interval_resp"][1])
        lower_interval_resp.append(temp["interval_resp"][0])
        upper_interval_custom.append(temp["interval_custom"][1])
        lower_interval_custom.append(temp["interval_custom"][0])
        upper_interval_dropped.append(temp["interval_dropped"][1])
        lower_interval_dropped.append(temp["interval_dropped"][0])

        print str(temp) + "\n"

    pyplot.close()
    Graphs.meanAndConfidenceInterval(roh, means_resp, lower_interval_resp, upper_interval_resp,
                                     "Average Response Time", "Packet Response Time")
    Graphs.meanAndConfidenceInterval(roh, means_custom, lower_interval_custom, upper_interval_custom,
                                     "Average Customers", "Customer Buffer Occupancy")
    Graphs.meanAndConfidenceInterval(roh, means_dropped, lower_interval_dropped, upper_interval_dropped,
                                     "Average Packet Dropped", "Packer Dropped")
    pyplot.show()
