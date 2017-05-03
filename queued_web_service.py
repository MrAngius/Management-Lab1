import simpy
import random

RANDOM_SEED = 42
INTER_ARRIVAL = 2.0
SERVICE_TIME = 18.0
NUM_PACKET = 100
BATCH = 10
MU_SERVICE = 12
LAMBDA_SERVICE = 10
SIM_TIME = 1000


class PacketArrival(object):

    # constructor
    def __init__(self, environ, arrival_time):

        # the inter-arrival time
        self.arrival_time = arrival_time

        # the environment
        self.env = environ

    # execute the process
    def arrival_process(self, buffer):
        while True:

            # sample the time to next arrival
            inter_arrival = random.expovariate(lambd=1.0/self.arrival_time)

            # yield an event to the simulator
            yield self.env.timeout(inter_arrival)

            # a packet has arrived
            self.env.process(buffer.run())


class Buffer(object):

    # constructor
    def __init__(self, environ, num_packet, service_time):

        # the service time
        self.service_time = service_time

        # batch
        self.batch = simpy.Resource(env, num_packet/10.0)

        # the environment
        self.env = environ

        # initialization of the buffer
        self.qsize = 0

    def run(self):
        print('A new batch has arrived at %7.4f' % self.env.now)

        self.qsize += 1

        # request's packet to be served
        with self.batch.request() as request:
            yield request

            while self.num_packet != 0:

                # once the packet is free, wait until service is finished
                service_time = random.expovariate(lambd=1.0/self.service_time)

                # yield an event to the simulator
                yield self.env.timeout(service_time)

                # decreasing number of requests in the batch
                self.num_packet -= 1

            # release the buffer
            self.qsize -= 1

        # the "with" statement implicitly delete request here "releasing" the resource


if __name__ == '__main__':

    random.seed(RANDOM_SEED)

    env = simpy.Environment()

    # packet arrival
    packet_arrival = PacketArrival(env, INTER_ARRIVAL)

    # buffer
    buffer = Buffer(env, NUM_PACKET, SERVICE_TIME)

    # start the arrival process
    env.process(packet_arrival.arrival_process(buffer))

    # simulate until SIM_TIME
    env.run(until=SIM_TIME)