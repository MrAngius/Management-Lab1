from simulation_p_1a import SimulateUsingBatches
from complex_queued_web_service import ComplexQueue
from scipy.stats import t
from graphs import Graphs
from matplotlib import pyplot
import numpy
import simpy


class SimulationAdvancedUsingBatches(SimulateUsingBatches):
    def __init__(self, lambda_arrival, mu_service, numb_services, confidence_interval, number_batches, queue_size,
                 a, b, warm_up=False):
        SimulateUsingBatches.__init__(self, lambda_arrival, mu_service, numb_services, confidence_interval,
                                      number_batches, warm_up)
        self.queue_size = queue_size
        self.a = a
        self.b = b
        self.mean_drop = None
        self.interval_drop = None

    def computeConfidenceDropped(self, index=0):
        self.stats[index].batchesAndWarmUp(self.number_batches, self.warm_up)
        batches_dropped_count = [sum(batch) for batch in self.stats[0].batches_dropped]
        mean_drop = numpy.mean(batches_dropped_count)
        std_drop = numpy.std(batches_dropped_count)

        interval_drop = t.interval(self.conf_interval, self.number_batches, loc=mean_drop, scale=std_drop)

        self.mean_drop, self.interval_drop = mean_drop, interval_drop

    def runSim(self):
        sim_time = self.BASE_SIM_TIME_BATCH * self.number_batches
        env = simpy.Environment()
        queue = ComplexQueue(self.mu_service, self.lambda_arrival, self.numb_services, env, self.stats[0],
                             self.stats[1], self.queue_size, self.a, self.b)
        env.process(queue.arrivals())
        env.run(until=sim_time)

        while True:
            if self.evaluateConfidenceOnTheFly():
                return 0
            else:
                sim_time = sim_time + self.BASE_SIM_TIME_BATCH
                env.run(until=sim_time)
                self.number_batches += 1

    def returnValuesSimulation(self):
        self.computeConfidenceDropped()

        return {"mean_resp": self.mean_response, "interval_resp": self.interval_response,
                "mean_custom": self.mean_customer, "interval_custom": self.interval_customer,
                "mean_dropped": self.mean_drop, "interval_dropped": self.interval_drop}


if __name__ == '__main__':
    LAMBDA_ARRIVAL = 60.0
    MU_SERVICE = 8.0
    SERVICE_NUMB = 1

    MIN_NUMB_BATCHES = 15
    CONFIDENCE_INTERVAL = 0.95
    SIZE = 50
    A = 3
    B = 6

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

    time_debug = 0

    for lambda_arr in lambda_arr_values:
        sim = SimulationAdvancedUsingBatches(lambda_arr, MU_SERVICE, SERVICE_NUMB, CONFIDENCE_INTERVAL,
                                             MIN_NUMB_BATCHES, SIZE, A, B, warm_up=True)
        sim.runSim()
        temp = sim.returnValuesSimulation()

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
        print str(time_debug) + "/" + str(len(lambda_arr_values)) + "\n"
        time_debug = time_debug + 1

    pyplot.close()
    Graphs.meanAndConfidenceInterval(roh, means_resp, lower_interval_resp, upper_interval_resp,
                                     "Average Response Time", "Packet Response Time")
    Graphs.meanAndConfidenceInterval(roh, means_custom, lower_interval_custom, upper_interval_custom,
                                     "Average Customers", "Customer Buffer Occupancy")
    Graphs.meanAndConfidenceInterval(roh, means_dropped, lower_interval_dropped, upper_interval_dropped,
                                     "Average Packet Dropped", "Packer Dropped")
    pyplot.show()
