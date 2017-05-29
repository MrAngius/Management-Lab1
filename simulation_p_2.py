from simulation_p_1b import SimulationAdvancedUsingBatches
from new_statistics import CustomerAverageStatistic, ResponseTimeAndDroppedStatistic
from front_back_server import WebAccelerator
from graphs import Graphs
from matplotlib import pyplot
from scipy.stats import t
import simpy
import numpy


class SimulationAdvancedCacheServer(SimulationAdvancedUsingBatches):
    def __init__(self, lambda_arrival, mu_service_front, mu_service_back, numb_services_front, numb_service_back,
                 confidence_interval, number_batches, queue_size_front, queue_size_back, a, b, hit_cache,
                 warm_up=False):
        SimulationAdvancedUsingBatches.__init__(self, lambda_arrival, mu_service_front, numb_services_front,
                                                confidence_interval, number_batches, queue_size_front, a, b, warm_up)
        self.mu_service_back = mu_service_back
        self.numb_services_back = numb_service_back
        self.queue_size_back = queue_size_back
        self.hit_cache = hit_cache
        self.stats = [ResponseTimeAndDroppedStatistic(), CustomerAverageStatistic(), CustomerAverageStatistic()]
        self.mean_customer_back = None
        self.interval_customer_back = None

    def runSim(self):
        sim_time = self.BASE_SIM_TIME_BATCH * self.number_batches
        env = simpy.Environment()
        queue = WebAccelerator(self.mu_service, self.mu_service_back, self.lambda_arrival, self.numb_services,
                               self.numb_services_back, env, self.stats[0], self.stats[1], self.stats[2],
                               self.queue_size, self.queue_size_back, self.a, self.b, self.hit_cache)
        env.process(queue.arrivals())
        env.run(until=sim_time)

        while True:
            if self.evaluateConfidenceOnTheFly():
                return 0
            else:
                sim_time = sim_time + self.BASE_SIM_TIME_BATCH
                env.run(until=sim_time)
                self.number_batches += 1

    def computeConfidenceCustomers_back(self):
        self.stats[2].batchesAndWarmUp(self.number_batches, self.warm_up)

        batches_customers_means = [CustomerAverageStatistic.customerAverage(batch)
                                   for batch in self.stats[2].batches_event_time_customers]
        mean_custom = numpy.mean(batches_customers_means)
        std_custom = numpy.std(batches_customers_means)
        interval_custom = t.interval(self.conf_interval, self.number_batches, loc=mean_custom, scale=std_custom)

        self.mean_customer_back, self.interval_customer_back = mean_custom, interval_custom

    def returnValuesSimulation(self):
        self.computeConfidenceDropped()
        self.computeConfidenceCustomers_back()
        return {"mean_resp": self.mean_response, "interval_resp": self.interval_response,
                "mean_custom_front": self.mean_customer, "interval_custom_front": self.interval_customer,
                "mean_custom_back": self.mean_customer_back, "interval_custom_back": self.interval_customer_back,
                "mean_dropped": self.mean_drop, "interval_dropped": self.interval_drop}


if __name__ == '__main__':
    LAMBDA_ARRIVAL_FRONT = 60.0
    MU_SERVICE_FRONT = 8.0
    MU_SERVICE_BACK = 10.0
    SERVICE_NUMB_FRONT = 1
    SERVICE_NUMB_BACK = 1
    HIT_CACHE = 30

    MIN_NUMB_BATCHES = 15
    CONFIDENCE_INTERVAL = 0.95
    SIZE_FRONT = 100
    SIZE_BACK = 50
    A = 3
    B = 6

    # vectors for statistics in the front queue
    means_resp_time = []
    means_custom_front = []
    means_dropped = []

    upper_interval_resp_time = []
    lower_interval_resp_time = []
    upper_interval_custom_front = []
    lower_interval_custom_front = []
    upper_interval_dropped = []
    lower_interval_dropped = []

    # vectors for statistics in the back queue
    means_custom_back = []
    upper_interval_custom_back = []
    lower_interval_custom_back = []

    lambda_arr_values = []
    roh = []
    lambda_arr = LAMBDA_ARRIVAL_FRONT

    # creation of the roh array
    while lambda_arr > MU_SERVICE_FRONT:
        lambda_arr_values.append(lambda_arr)
        roh.append(MU_SERVICE_FRONT / lambda_arr)
        lambda_arr -= 0.5

    time_debug = 0

    for lambda_arr in lambda_arr_values:
        sim = SimulationAdvancedCacheServer(lambda_arr, MU_SERVICE_FRONT, MU_SERVICE_BACK, SERVICE_NUMB_FRONT,
                                            SERVICE_NUMB_BACK, CONFIDENCE_INTERVAL, MIN_NUMB_BATCHES, SIZE_FRONT,
                                            SIZE_BACK, A, B, HIT_CACHE, warm_up=False)
        sim.runSim()
        temp = sim.returnValuesSimulation()

        # saving the data in separate lists for front
        means_resp_time.append(temp["mean_resp"])
        means_custom_front.append(temp["mean_custom_front"])
        upper_interval_resp_time.append(temp["interval_resp"][1])
        lower_interval_resp_time.append(temp["interval_resp"][0])
        upper_interval_custom_front.append(temp["interval_custom_front"][1])
        lower_interval_custom_front.append(temp["interval_custom_front"][0])
        means_dropped.append(temp["mean_dropped"])
        upper_interval_dropped.append(temp["interval_dropped"][1])
        lower_interval_dropped.append(temp["interval_dropped"][0])

        # saving the data in separate lists for back
        means_custom_back.append(temp["mean_custom_back"])
        upper_interval_custom_back.append(temp["interval_custom_back"][1])
        lower_interval_custom_back.append(temp["interval_custom_back"][0])

        print str(temp) + "\n"
        print str(time_debug) + "/" + str(len(lambda_arr_values)) + "\n"
        time_debug = time_debug + 1

    pyplot.close()
    Graphs.meanAndConfidenceInterval(roh, means_resp_time, lower_interval_resp_time, upper_interval_resp_time,
                                     "Average Response Time", "Packet Response Time Front Server")
    Graphs.meanAndConfidenceInterval(roh, means_custom_front, lower_interval_custom_front, upper_interval_custom_front,
                                     "Average Customers", "Customer Buffer Occupancy Front Server")
    Graphs.meanAndConfidenceInterval(roh, means_dropped, lower_interval_dropped,
                                     upper_interval_dropped,
                                     "Average Packet Dropped", "Packer Dropped Front Server")
    Graphs.meanAndConfidenceInterval(roh, means_custom_back, lower_interval_custom_back, upper_interval_custom_back,
                                     "Average Customers", "Customer Buffer Occupancy Back Server")

    pyplot.show()
