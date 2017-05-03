import simpy
import numpy
from scipy.stats import t
from statistic_collector import Statistics
from statistic_collector import CustomerAverage
from simplified_web_service import Queue
from graphs import Graphs
from matplotlib import pyplot


def averageCustomers(batch):
    """function provided for manage the mean of each batch"""
    # the first element of the vector is a tuple which has the time of the event as first value
    time = batch[0][0]
    customers_avg = CustomerAverage(initial_time=time)
    for data in batch:
        customers_avg.update(data[0], data[1])

    return customers_avg.mean(list(batch).pop()[0])


class SimulationRoh(object):
    """class used to define a number of runs, observations, implemented using a batch-style approach"""

    def __init__(self, lambda_arrival, mu_service, numb_services, confidence_interval, warm_up=False):
        self.lambda_arrival = lambda_arrival
        self.mu_service = mu_service
        self.numb_services = numb_services
        self.conf_interval = confidence_interval
        self.warm_up = warm_up

    def runSim(self, long_sim=False):
        """run the simulation for extracting an observation of the process"""
        if long_sim:
            sim_time = 10000 * 10
        else:
            sim_time = 10000

        rand_seed = 50
        env = simpy.Environment()
        stats = Statistics()

        queue = Queue(self.mu_service, self.lambda_arrival, self.numb_services, rand_seed, env, stats)
        env.process(queue.arrivals())
        env.run(until=sim_time)

        return stats

    def confidenceIntervalResults(self, numb_batches, p=0.2, dynamic_batch=False):
        """compute the student's t confidence interval and iterate increasing the batches if the interval is wide"""
        n = numb_batches
        z_resp = 100
        z_custom = 100
        interval_resp = []
        interval_custom = []
        mean_resp = 100.0
        mean_custom = 100.0

        stats = self.runSim(long_sim=True)

        # implementing the batch number computing the confidence interval on-the-fly
        while (2 * z_resp / mean_resp) > p and (2 * z_custom / mean_custom) > p:

            batches_response = stats.batchesResponseTime(n)
            batches_customers = stats.batchesCustomerQueue(n)

            batches_response_means = [numpy.mean(batch) for batch in batches_response]
            batches_customers_means = [averageCustomers(batch) for batch in batches_customers]

            mean_resp = numpy.mean(batches_response_means)
            mean_custom = numpy.mean(batches_customers_means)

            std_custom = numpy.std(batches_customers_means)
            std_resp = numpy.std(batches_response_means)

            interval_resp = t.interval(self.conf_interval, n, loc=mean_resp, scale=std_resp)
            interval_custom = t.interval(self.conf_interval, n, loc=mean_custom, scale=std_custom)

            z_resp = interval_resp[1] - mean_resp
            z_custom = interval_custom[1] - mean_custom

            # ___debug___

            print n
            print std_resp, std_custom

            n += 1

            if not dynamic_batch:
                return {"mean_resp": mean_resp, "interval_resp": interval_resp,
                        "mean_custom": mean_custom, "interval_custom": interval_custom}

        return {"mean_resp": mean_resp, "interval_resp": interval_resp,
                "mean_custom": mean_custom, "interval_custom": interval_custom}


if __name__ == '__main__':
    LAMBDA_ARRIVAL = 10
    MU_SERVICE = 8.0
    SERVICE_NUMB = 1
    CONFIDENCE_INTERVAL = 0.95

    # vectors for collecting data
    means_resp = []
    means_custom = []
    upper_interval_resp = []
    lower_interval_resp = []
    upper_interval_custom = []
    lower_interval_custom = []

    lambda_arr_values = []
    roh = []
    lambda_arr = 10.0

    # creation of the roh array
    while lambda_arr > MU_SERVICE:
        lambda_arr_values.append(lambda_arr)
        roh.append(MU_SERVICE / lambda_arr)
        lambda_arr -= 0.02

    for lambda_arr in lambda_arr_values:
        sim = SimulationRoh(lambda_arr, MU_SERVICE, SERVICE_NUMB, CONFIDENCE_INTERVAL)
        temp = sim.confidenceIntervalResults(25)

        # saving the data in separate lists
        means_resp.append(temp["mean_resp"])
        means_custom.append(temp["mean_custom"])
        upper_interval_resp.append(temp["interval_resp"][1])
        lower_interval_resp.append(temp["interval_resp"][0])
        upper_interval_custom.append(temp["interval_custom"][1])
        lower_interval_custom.append(temp["interval_custom"][0])

        print str(temp) + "\n"

    pyplot.close()
    Graphs.meanAndConfidenceInterval(roh, means_resp, lower_interval_resp, upper_interval_resp,
                                     "Average Response Time", "Packet Response Time")
    Graphs.meanAndConfidenceInterval(roh, means_custom, lower_interval_custom, upper_interval_custom,
                                     "Average Customers", "Customer Buffer Occupancy")
    pyplot.show()
