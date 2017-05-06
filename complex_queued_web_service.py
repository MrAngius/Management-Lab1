import simplified_web_service as sw
import random
import numpy


class ComplexQueue(sw.Queue):
    def __init__(self, service_time, arrival_time, num_service, size, a, b, seed, environment, statistics):
        super(ComplexQueue, self).__init__(service_time, arrival_time, num_service, seed, environment, statistics)
        self.queue_size = size
        self.a = a
        self.b = b

    def arrivals(self):
        while True:
            # create the batch
            batch = Batch(self.a, self.b)

            # call the service for each batch
            # counter based on batch size

            # we compute the arrival time for the batch
            inter_arrival = random.expovariate(lambd=1.0 / self.arrival_time)

            # wait until a new batch arrives
            yield self.env.timeout(inter_arrival)

            # assuming the same time for all packets in the batch
            t = self.env.now
            free_space = self.queue_size - len(self.services.queue)

            if batch.batch_size > free_space:

                # save the dropped packets
                dropped = numpy.abs(batch.batch_size - free_space)

                for k in range(free_space):
                    # STATISTICS
                    self.statistics.updateArrival(t)
                    self.statistics.newArrival()
                    # update the customer average when a new packet has arrived
                    self.statistics.averageCustomersUpdate(t, len(self.services.queue))

                    # call the service for a packet in the batch
                    self.env.process(self.service())

                # increase the number of dropped packets
                self.statistics.updateDropped(dropped)

            else:

                for k in range(batch.batch_size):
                    # STATISTICS
                    self.statistics.updateArrival(t)
                    self.statistics.newArrival()
                    # update the customer average when a new packet has arrived
                    self.statistics.averageCustomersUpdate(t, len(self.services.queue))

                    # call the service for a packet in the batch
                    self.env.process(self.service())
                # save also the zero drop case in the vector
                self.statistics.updateDropped(0)

    def service(self):
        return super(ComplexQueue, self).service()


class Batch(object):

    def __init__(self, a, b):
        self.batch_size = random.randint(a, b)
