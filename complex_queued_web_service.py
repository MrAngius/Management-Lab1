import simplified_web_service as sw
import random


class ComplexQueue(sw.Queue):
    def __init__(self, service_time, arrival_time, num_service, environment, service_stats, customer_stats,
                 size, a, b):
        sw.Queue.__init__(self, service_time, arrival_time, num_service, environment, service_stats, customer_stats)
        self.queue_size = size
        self.a = a
        self.b = b

    def arrivals(self, packet=None):
        while True:
            # create the batch
            batch = self.Batch(self.a, self.b)
            inter_arrival = random.expovariate(lambd=1.0 / self.arrival_time)
            yield self.env.timeout(inter_arrival)

            # assuming the same time for all packets in the batch
            env_time = self.env.now
            free_space = self.queue_size - len(self.services.queue)
            # print "\n queue size: " + str(len(self.services.queue)) + "\n"

            dropped = batch.batch_size - free_space
            if dropped > 0:
                for k in range(free_space):
                    self.callForService(inter_arrival, env_time)
                # for cycle to create as many packet as the dropped ones
                for j in range(dropped):
                    self.dropPackets(inter_arrival, env_time)
            else:
                for k in range(batch.batch_size):
                    self.callForService(inter_arrival, env_time)

    def dropPackets(self, inter_arrival, env_time):
        # STATISTICS
        packet = self.Packet()
        # update the dropped status
        packet.dropped = True
        packet.addTimeService(env_time)
        packet.computed_arrival = inter_arrival
        self.service_stats.addPacket(packet)

    # inner class
    class Batch:
        def __init__(self, a, b):
            self.batch_size = random.randint(a, b)
