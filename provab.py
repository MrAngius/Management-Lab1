import simpy
import random

class BatchArrival(object):
    def __init__(self, arrival_time, environ, seed):
        # holds samples of inter-arrival time
        self.inter_arrival = []
        self.arrival_time = arrival_time
        self.env = environ
        random.seed(seed)

    def arrivals(self, queue):
        while True:
            # we compute the arrival time
            inter_arrival = random.expovariate(lambd=1.0 / self.arrival_time)

            # wait until a new batch arrives
            yield self.env.timeout(inter_arrival)

            # call the service for a packet
            self.env.process(queue.service())

class QueueModel(object):

    def __init__(self, service_time, num_packet, queue, seed, environment):
        self.batch = simpy.Resource(environment, num_packet)
        self.service_time = service_time
        self.queue = queue
        self.instant_boccupancy = 0
        self.queue_occupancy = 0
        self.env = environment
        random.seed(seed)

    def service(self, batch_size):

        with self.batch.request() as request:
            self.instant_boccupancy += 1
            # this hold the request until the service is busy
            yield request
            self.instant_boccupancy -= 1
            # occupacy
            queue_occupancy = MAX_QUEUE_SIZE - batch_size
            if queue_occupancy ==0:
                yield self.env.timeout(0)
            else:
                # when the service is no more busy, we compute the service time
                service_time = random.expovariate(lambd=1.0 / self.service_time)
                # wait util the service won't finish
                yield self.env.timeout(service_time)
                # updating queue size
                queue_occupancy -=1

class Batch(object):

    def __init__(self):
        self.batch_size = random.randint(*NUM_PACKET)

if __name__ == '__main__':
    LAMBDA_ARRIVAL = 11
    MU_SERVICE = 8
    SIM_TIME = 1000
    RANDOM_SEED = 42
    SERVICE_NUMB = 1
    NUM_PACKET = [1, 20]
    MAX_QUEUE_SIZE = 30

    env = simpy.Environment()

    queue = QueueModel(MU_SERVICE, LAMBDA_ARRIVAL, SERVICE_NUMB, RANDOM_SEED, env)
    env.process(queue.arrivals(queue))


    env.run(until=SIM_TIME)