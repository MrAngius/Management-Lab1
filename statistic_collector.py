import numpy
import math


class Statistics(object):
    """class used to evaluate statistics in our simulation"""

    def __init__(self):
        self.vector_time_arrival = []
        self.vector_time_service = []
        self.vector_packet_dropped = []
        self.packet_arrived = 0
        self.packet_served = 0
        self.avg_number_customer = CustomerAverage()
        self.customer_buffer = []

    def newArrival(self):
        self.packet_arrived += 1

    def newServed(self):
        self.packet_served += 1

    def updateDropped(self, packets_dropped):
        """update the vector of packet dropped"""
        self.vector_packet_dropped.append(packets_dropped)

    def updateArrival(self, arrival_time):
        """update the vector of arrival-time"""
        self.vector_time_arrival.append(arrival_time)

    def updateService(self, service_time):
        """update the vector of service-time"""
        self.vector_time_service.append(service_time)

    def averageCustomersUpdate(self, current_time, waiting_customers):
        """save for each event the time and the number of customers in the queue"""
        self.customer_buffer.append((current_time, waiting_customers))

    def computeAverageCustomers(self):
        """return the average of customers in the queue"""
        for data in self.customer_buffer:
            self.avg_number_customer.update(data[0], data[1])

        return self.avg_number_customer.mean(self.customer_buffer.pop()[0])

    def computeAverageResponseTime(self):
        """compute the mean of the response times for customers"""
        return numpy.mean(self.extractResponseTime())

    def extractResponseTime(self):
        """extract a vector of response time for the system"""
        temp = []
        for service, arrival in zip(self.vector_time_service, self.vector_time_arrival):
            temp.append(service - arrival)
        return temp

    def extractCustomersNumberQueue(self):
        """extract the number of customer in the queue updated for each event occurrence"""
        temp = []
        for element in self.customer_buffer:
            temp.append(element[1])
        return temp

    def batchesResponseTime(self, numb_batches, warm_up=False):
        """extract a list of batches for the response time from a long vector of samples"""
        if warm_up:
            response_time = self.extractResponseTime()
            worm_cut = WarmUpCut(0.01)
            cut_response_vector = worm_cut.eliminateWarmUpResponseTime(response_time)
            temp = zip(*[iter(cut_response_vector)] * int(math.ceil(len(cut_response_vector) / numb_batches)))
            if len(temp) > numb_batches:
                temp.pop()
                return temp
            return temp
        else:
            response_time = self.extractResponseTime()
            temp = zip(*[iter(response_time)] * int(math.ceil(len(response_time) / numb_batches)))
            if len(temp) > numb_batches:
                temp.pop()
                return temp
            return temp

    def batchesCustomerQueue(self, numb_batches, warm_up=False):
        """extract a list of batches for the number of customer in the queue from a long vector of samples"""
        if warm_up:
            pass
        else:
            customers = self.customer_buffer
            temp = zip(*[iter(customers)] * int(math.ceil(len(customers) / numb_batches)))
            if len(temp) > numb_batches:
                temp.pop()
                return temp
            return temp

    def batchesDroppedPackets(self, numb_batches, warm_up=False):
        """extract a list of batches for the number of customer in the queue from a long vector of samples"""
        if warm_up:
            pass
        else:
            temp = zip(*[iter(self.vector_packet_dropped)]
                        * int(math.ceil(len(self.vector_packet_dropped) / numb_batches)))

            if len(temp) > numb_batches:
                temp.pop()
                return temp
            return temp


class CustomerAverage(object):
    """class used to implement the time-average-like computation, in this case for customers in the queue"""

    def __init__(self, initial_time=0.0):
        self.total_area = 0.0
        self.old_sample = 0.0
        self.last_time = initial_time
        self.initial_time = initial_time

    def update(self, current_time, current_sample):
        """implementation of the time average"""
        delta_time = float(current_time) - self.last_time
        self.total_area += self.old_sample * delta_time
        self.old_sample = current_sample
        self.last_time = current_time

    def mean(self, final_time):
        """computation of the mean"""
        return self.total_area / (final_time - self.initial_time)


class WarmUpCut(object):
    """class used to eliminate the transient in the acquired data performing an iterative comparison"""

    def __init__(self, stop_delta, k=10):
        self.stop_delta = stop_delta
        self.k = k
        self.previous_mean = 0.0
        self.delta = 1

    def eliminateWarmUpResponseTime(self, vector_data):
        """iterate over the vector and compare the average in order to check for the steady state samples"""
        temp_vector = []

        while self.delta > self.stop_delta:
            temp_vector = vector_data[self.k * 10:]
            temp_mean = numpy.mean(temp_vector)
            self.delta = abs((temp_mean - self.previous_mean) / temp_mean)
            self.previous_mean = temp_mean
            self.k += 1

        return temp_vector

    def eliminateWarmUpCustomer(self):
        """iterate over the vector and compare the average in order to check for the steady state samples"""
        pass
