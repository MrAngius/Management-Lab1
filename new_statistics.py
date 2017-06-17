import math


class ResponseTimeAndDroppedStatistic:
    def __init__(self):
        self.packets = []
        # values extracted from the packets
        self.response_times = []
        self.packets_dropped = []
        # to save the created batches
        self.batches_response_time = []
        self.batches_dropped = []
        self.warm_upped = False
        self.computed_dropped = False
        self.computed_response = False
        self.packet_arrived = 0

    def addPacket(self, packet):
        self.packets.append(packet)
        self.computed_response = False
        self.computed_dropped = False
        self.packet_arrived += 1

    def batchesAndWarmUp(self, num_batches, warm_up=False):
        self.computeDroppedPackets()
        self.computeResponseTime()
        self.batchesDroppedAndNonDroppedPackets(num_batches)
        self.batchesResponseTime(num_batches)
        if warm_up:
            self.eliminateWarmUpResponseTimeAndDropped()

    def computeResponseTime(self):
        self.response_times = [reduce(lambda a, b: a + b, x.extractResponseTime()) for x in self.packets if
                               not x.dropped]
        self.computed_response = True
        if self.computed_dropped:
            self.packets = []

    def computeDroppedPackets(self):
        self.packets_dropped = map(lambda y: 1 if y else 0, [x.dropped for x in self.packets])
        self.computed_dropped = True
        if self.computed_response:
            self.packets = []

    def batchesResponseTime(self, numb_batches):
        new_batches_numb = numb_batches - len(self.batches_response_time)
        if new_batches_numb > 0:
            temp = zip(*[iter(self.response_times)] * int(math.ceil(len(self.response_times) / numb_batches)))
            self.response_times = []
            if len(temp) > numb_batches:
                temp.pop()
                for batch in temp:
                    self.batches_response_time.append(batch)
            for batch in temp:
                self.batches_response_time.append(batch)

    def batchesDroppedAndNonDroppedPackets(self, numb_batches):
        new_batches_numb = numb_batches - len(self.batches_dropped)
        if new_batches_numb > 0:
            temp = zip(*[iter(self.packets_dropped)] * int(math.ceil(len(self.packets_dropped) / new_batches_numb)))

            if len(temp) > numb_batches:
                temp.pop()
                for batch in temp:
                    self.batches_dropped.append(batch)
            for batch in temp:
                self.batches_dropped.append(batch)

    def eliminateWarmUpResponseTimeAndDropped(self):
        if not self.warm_upped:
            self.batches_response_time.pop(0)
            self.batches_dropped.pop(0)
            self.warm_upped = True


class CustomerAverageStatistic:
    def __init__(self):
        self.event_time_customers = []
        self.batches_event_time_customers = []
        self.warm_upped = False

    def eventRegistration(self, event_time, number_customers):
        self.event_time_customers.append((event_time, number_customers))

    def batchesAndWarmUp(self, numb_batches, warm_up=False):
        self.batchesCustomerQueue(numb_batches)
        if warm_up:
            self.eliminateWarmUp()

    def batchesCustomerQueue(self, numb_batches):
        new_batch_number = numb_batches - len(self.batches_event_time_customers)
        if new_batch_number > 0:
            temp = zip(*[iter(self.event_time_customers)] * int(math.ceil(len(self.event_time_customers)
                                                                          / new_batch_number)))
            if len(temp) > numb_batches:
                temp.pop()
                for batch in temp:
                    self.batches_event_time_customers.append(batch)
            for batch in temp:
                self.batches_event_time_customers.append(batch)

    def eliminateWarmUp(self):
        if not self.warm_upped:
            self.batches_event_time_customers.pop(0)
            self.warm_upped = True

    @staticmethod
    def customerAverage(batch):
        total_area = 0.0
        old_sample = batch[0][1]
        last_time = batch[0][0]

        for sample in batch:
            delta_time = sample[0] - last_time
            total_area += old_sample * delta_time
            old_sample = sample[1]
            # update the last time
            last_time = sample[0]

        return total_area / (batch[-1][0] - batch[0][0])
