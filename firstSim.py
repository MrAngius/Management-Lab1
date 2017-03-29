import simpy
import random

CAR_ARRIVAL = 2
TRUCK_ARRIVAL = 3
SIM_TIME = 100


def arrival_process(environment, vehicle, arrival_time):
    inter_arrival = random.expovariate(lambd=1.0/arrival_time)

    yield environment.timeout(inter_arrival)

    print "The event has occurred: a {} has arrived at {}".format(vehicle, environment.now)


env = simpy.Environment()

env.process(arrival_process(env, "CAR", CAR_ARRIVAL))
env.process(arrival_process(env, "TRUCK", TRUCK_ARRIVAL))

env.run(until=SIM_TIME)