from new_statistics import ResponseTimeAndDroppedStatistic, CustomerAverageStatistic
from scipy.stats import t
from simplified_web_service import Queue
from graphs import Graphs
from matplotlib import pyplot
import simpy
import numpy


class SimulateUsingBatches:
    BASE_SIM_TIME_BATCH = 10000

    def __init__(self, lambda_arrival, mu_service, numb_services, confidence_interval, number_batches, warm_up=False):
        self.lambda_arrival = lambda_arrival
        self.mu_service = mu_service
        self.numb_services = numb_services
        self.conf_interval = confidence_interval
        self.warm_up = warm_up
        self.stats = [ResponseTimeAndDroppedStatistic(), CustomerAverageStatistic()]
        self.number_batches = number_batches

        self.mean_customer = None
        self.mean_response = None
        self.interval_customer = None
        self.interval_response = None

    def returnValuesSimulation(self):
        return {"mean_resp": self.mean_response, "interval_resp": self.interval_response,
                "mean_custom": self.mean_customer, "interval_custom": self.interval_customer}

    def runSim(self):
        sim_time = self.BASE_SIM_TIME_BATCH * self.number_batches
        env = simpy.Environment()
        queue = Queue(self.mu_service, self.lambda_arrival, self.numb_services, env, self.stats[0], self.stats[1])
        env.process(queue.arrivals())
        env.run(until=sim_time)

        while True:
            if self.evaluateConfidenceOnTheFly():
                return 0
            else:
                sim_time = sim_time + self.BASE_SIM_TIME_BATCH
                env.run(until=sim_time)
                self.number_batches += 1

    def evaluateConfidenceOnTheFly(self):
        # implementing the batch number computing the confidence interval on-the-fly
        self.computeConfidenceCustomers()
        self.computeConfidenceResponse()

        z_customer = self.interval_customer[1] - self.interval_customer[0]
        z_service = self.interval_response[1] - self.interval_response[0]

        print (z_service / self.mean_response)

        if (z_customer / self.mean_customer) > self.conf_interval \
                and (z_service / self.mean_response) > self.conf_interval:
            if self.number_batches == 31:
                return True
            else:
                return False
        else:
            return True

    def computeConfidenceCustomers(self):
        self.stats[1].batchesAndWarmUp(self.number_batches, self.warm_up)

        batches_customers_means = [CustomerAverageStatistic.customerAverage(batch)
                                   for batch in self.stats[1].batches_event_time_customers]
        mean_custom = numpy.mean(batches_customers_means)
        std_custom = numpy.std(batches_customers_means)
        interval_custom = t.interval(self.conf_interval, self.number_batches, loc=mean_custom, scale=std_custom)

        self.mean_customer, self.interval_customer = mean_custom, interval_custom

    def computeConfidenceResponse(self):
        self.stats[0].batchesAndWarmUp(self.number_batches, self.warm_up)

        batches_response_means = [numpy.mean(batch) for batch in self.stats[0].batches_response_time]
        mean_resp = numpy.mean(batches_response_means)
        std_resp = numpy.std(batches_response_means)
        interval_resp = t.interval(self.conf_interval, self.number_batches, loc=mean_resp, scale=std_resp)

        self.mean_response, self.interval_response = mean_resp, interval_resp

if __name__ == '__main__':
    LAMBDA_ARRIVAL = 10
    MU_SERVICE = 8.0
    SERVICE_NUMB = 1

    MIN_NUMB_BATCHES = 15
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
        sim = SimulateUsingBatches(lambda_arr, MU_SERVICE, SERVICE_NUMB, CONFIDENCE_INTERVAL, MIN_NUMB_BATCHES)
        sim.runSim()
        temp = sim.returnValuesSimulation()

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
