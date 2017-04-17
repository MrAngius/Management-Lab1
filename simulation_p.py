import simpy
import numpy
from scipy.stats import t
from statistic_collector import Statistics
from simplified_web_service import Queue


class SimulationRoh(object):
    """class used to define a number of runs, observations, implemented using a batch-style approach"""

    def __init__(self, lambda_arrival, mu_service, numb_services, confidence_interval, warm_up=False):
        self.lambda_arrival = lambda_arrival
        self.mu_service = mu_service
        self.numb_services = numb_services
        self.conf_interval = confidence_interval
        self.warm_up = warm_up

    def runSim(self, numb_batches=10):
        """run the simulation for extracting an observation of the process"""
        sim_time = 1000000 * numb_batches
        rand_seed = 500
        env = simpy.Environment()
        stats = Statistics()

        queue = Queue(self.mu_service, self.lambda_arrival, self.numb_services, rand_seed, env, stats)
        env.process(queue.arrivals())
        env.run(until=sim_time)

        return stats

    def confidenceIntervalResults(self, numb_batches, p):
        """compute the student's t confidence interval and iterate increasing the batches if the interval is wide"""
        n = numb_batches
        z = 100
        interval = []
        mean = 0.0

        while 2 * z / mean > p:
            batches = self.runSim(n).batchesResponseTime(n)
            batches_mean = [numpy.mean(batch) for batch in batches]
            mean = numpy.mean(batches_mean)
            std = numpy.std(batches_mean)
            interval = t.interval(self.conf_interval, n, loc=mean, scale=std)
            z = interval[1] - mean
            n += 1
            print n
            if n == 25:
                return {"mean": mean, "interval": interval}

        return {"mean": mean, "interval": interval}
