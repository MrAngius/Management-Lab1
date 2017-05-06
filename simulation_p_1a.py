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
    BASE_SIM_TIME_BATCH = 10000

    def __init__(self, lambda_arrival, mu_service, numb_services, confidence_interval, warm_up=False):
        self.lambda_arrival = lambda_arrival
        self.mu_service = mu_service
        self.numb_services = numb_services
        self.conf_interval = confidence_interval
        self.warm_up = warm_up

    def runSim(self, n=10):
        """run the simulation for extracting an observation of the process"""

        sim_time = self.BASE_SIM_TIME_BATCH * n

        rand_seed = 50
        env = simpy.Environment()

        statistics = Statistics()

        queue = Queue(self.mu_service, self.lambda_arrival, self.numb_services, rand_seed, env, statistics)
        env.process(queue.arrivals())
        env.run(until=sim_time)

        while True:
            if self.computeConfidenceOnTheFly(statistics, n):
                return statistics, n
            else:
                sim_time = sim_time + self.BASE_SIM_TIME_BATCH
                env.run(until=sim_time)
                n = n + 1

    def computeConfidenceOnTheFly(self, statistics, n=10, p=0.2, final_result=False):

        batches_response = statistics.batchesResponseTime(n)
        batches_customers = statistics.batchesCustomerQueue(n)

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

        # implementing the batch number computing the confidence interval on-the-fly
        if final_result:
            return {"mean_resp": mean_resp, "interval_resp": interval_resp,
                    "mean_custom": mean_custom, "interval_custom": interval_custom}
        elif (2 * z_resp / mean_resp) > p and (2 * z_custom / mean_custom) > p:

            print n, (2 * z_resp / mean_resp), (2 * z_custom / mean_custom), "\n"
            if n == 30:
                return True
            return False
        else:
            return True

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
        stats, batch_num = sim.runSim(n=25)
        temp = sim.computeConfidenceOnTheFly(stats, batch_num, final_result=True)

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
