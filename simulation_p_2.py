from front_back_server import FrontEndServer, BackEndServer
from simulation_p_1b import SimulationRohComplex
from statistic_collector import Statistics
from graphs import Graphs
from matplotlib import pyplot
import simpy


class SimulationRohCache(SimulationRohComplex):
    def __init__(self, lambda_arrival, mu_service_front, mu_service_back, numb_services, confidence_interval,
                 size, hit_cache, warm_up=False):
        super(SimulationRohCache, self).__init__(lambda_arrival, mu_service_front, numb_services, confidence_interval,
                                                 size, None, None, warm_up)
        self.mu_service_back = mu_service_back
        self.mu_service_front = mu_service_front
        self.hit_cache = hit_cache

    def runSim(self, n=10):
        sim_time = self.BASE_SIM_TIME_BATCH * n

        rand_seed = 50
        env = simpy.Environment()

        statistics_front = Statistics()
        statistics_back = Statistics()

        back_server = BackEndServer(self.mu_service_back, self.numb_services, self.size, self.a, self.b,
                                    rand_seed, env, statistics_back)

        front_server = FrontEndServer(self.mu_service_front, self.lambda_arrival, self.numb_services, self.size,
                                      self.a, self.b, rand_seed, env, statistics_front, back_server,
                                      hit_cache=self.hit_cache)

        env.process(front_server.arrivals())
        env.run(until=sim_time)

        while True:
            if self.computeConfidenceOnTheFly(statistics_front, n):
                return statistics_front, statistics_back, n
            else:
                sim_time = sim_time + self.BASE_SIM_TIME_BATCH
                env.run(until=sim_time)
                n = n + 1


if __name__ == '__main__':
    LAMBDA_ARRIVAL_FRONT = 10.0
    MU_SERVICE_FRONT = 8.0
    MU_SERVICE_BACK = 30.0
    SERVICE_NUMB = 1
    CONFIDENCE_INTERVAL = 0.95
    HIT_CACHE = 99
    SIZE = 100

    # vectors for statistics in the front queue
    means_resp_front = []
    means_custom_front = []
    means_dropped_front = []

    upper_interval_resp_front = []
    lower_interval_resp_front = []
    upper_interval_custom_front = []
    lower_interval_custom_front = []
    upper_interval_dropped_front = []
    lower_interval_dropped_front = []

    # vectors for statistics in the back queue
    means_resp_back = []
    means_custom_back = []
    means_dropped_back = []

    upper_interval_resp_back = []
    lower_interval_resp_back = []
    upper_interval_custom_back = []
    lower_interval_custom_back = []
    upper_interval_dropped_back = []
    lower_interval_dropped_back = []

    lambda_arr_values = []
    roh = []
    lambda_arr = LAMBDA_ARRIVAL_FRONT

    # creation of the roh array
    while lambda_arr > MU_SERVICE_FRONT:
        lambda_arr_values.append(lambda_arr)
        roh.append(MU_SERVICE_FRONT / lambda_arr)
        lambda_arr -= 0.03

    time_debug = 0

    for lambda_arr in lambda_arr_values:
        sim = SimulationRohCache(lambda_arr, MU_SERVICE_FRONT, MU_SERVICE_BACK, SERVICE_NUMB,
                                 CONFIDENCE_INTERVAL, SIZE, HIT_CACHE)
        stats_front, stats_back, batch_num = sim.runSim(n=30)
        temp_front = sim.computeConfidenceOnTheFly(stats_front, batch_num, final_result=True)
        temp_back = sim.computeConfidenceOnTheFly(stats_back, batch_num, final_result=True)

        # saving the data in separate lists for front
        means_resp_front.append(temp_front["mean_resp"])
        means_custom_front.append(temp_front["mean_custom"])
        means_dropped_front.append(temp_front["mean_dropped"])
        upper_interval_resp_front.append(temp_front["interval_resp"][1])
        lower_interval_resp_front.append(temp_front["interval_resp"][0])
        upper_interval_custom_front.append(temp_front["interval_custom"][1])
        lower_interval_custom_front.append(temp_front["interval_custom"][0])
        upper_interval_dropped_front.append(temp_front["interval_dropped"][1])
        lower_interval_dropped_front.append(temp_front["interval_dropped"][0])

        # saving the data in separate lists for back
        means_resp_back.append(temp_back["mean_resp"])
        means_custom_back.append(temp_back["mean_custom"])
        means_dropped_back.append(temp_back["mean_dropped"])
        upper_interval_resp_back.append(temp_back["interval_resp"][1])
        lower_interval_resp_back.append(temp_back["interval_resp"][0])
        upper_interval_custom_back.append(temp_back["interval_custom"][1])
        lower_interval_custom_back.append(temp_back["interval_custom"][0])
        upper_interval_dropped_back.append(temp_back["interval_dropped"][1])
        lower_interval_dropped_back.append(temp_back["interval_dropped"][0])

        print str(temp_front) + "\n"
        print str(temp_back) + "\n"
        print str(time_debug) + "/" + str(len(lambda_arr_values)) + "\n"
        time_debug = time_debug + 1

    pyplot.close()
    Graphs.meanAndConfidenceInterval(roh, means_resp_front, lower_interval_resp_front, upper_interval_resp_front,
                                     "Average Response Time", "Packet Response Time Front Server")
    Graphs.meanAndConfidenceInterval(roh, means_custom_front, lower_interval_custom_front, upper_interval_custom_front,
                                     "Average Customers", "Customer Buffer Occupancy Front Server")
    Graphs.meanAndConfidenceInterval(roh, means_dropped_front, lower_interval_dropped_front,
                                     upper_interval_dropped_front,
                                     "Average Packet Dropped", "Packer Dropped Front Server")
    Graphs.meanAndConfidenceInterval(roh, means_resp_back, lower_interval_resp_back, upper_interval_resp_back,
                                     "Average Response Time", "Packet Response Time Back Server")
    Graphs.meanAndConfidenceInterval(roh, means_custom_back, lower_interval_custom_back, upper_interval_custom_back,
                                     "Average Customers", "Customer Buffer Occupancy Back Server")
    # Graphs.meanAndConfidenceInterval(roh, means_dropped_back, lower_interval_dropped_back,
    #                                  upper_interval_dropped_front,
    #                                  "Average Packet Dropped", "Packer Dropped Back Server")

    pyplot.show()
