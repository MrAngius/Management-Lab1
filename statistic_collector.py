# definition of classes used to evaluate statistics in our simulation
import numpy


class Statistics(object):
    def __init__(self):
        self.vector_time_arrival = []
        self.vector_time_service = []
        self.packet_arrived = 0
        self.packet_dropped = 0
        self.packet_served = 0
        self.avg_number_customer = CustomerAverage()
        self.event_buffer = []

    def newArrival(self):
        self.packet_arrived += 1

    def newServed(self):
        self.packet_served += 1

    def newDropped(self):
        self.packet_dropped += 1

    def updateArrival(self, arrival_time):
        """update the vector of arrival-time"""
        self.vector_time_arrival.append(arrival_time)

    def updateService(self, service_time):
        """update the vector of service-time"""
        self.vector_time_service.append(service_time)

    def averageCustomersUpdate(self, current_time, waiting_customers):
        """save for each event the time and the number of customers in the queue"""
        self.event_buffer.append((current_time, waiting_customers))

    def computeAverageCustomers(self):
        """return the average of customers in the queue"""
        for data in self.event_buffer:
            self.avg_number_customer.update(data[0], data[1])

        return self.avg_number_customer.mean(self.event_buffer.pop()[0])

    def extractResponseTime(self):
        """extract a vector of response time for the system"""
        temp = []
        for service, arrival in zip(self.vector_time_service, self.vector_time_arrival):
            temp.append(service - arrival)
        return temp

    def computeAverageResponseTime(self):
        """compute the mean of the response times for customers"""

        return numpy.mean(self.extractResponseTime())

    def extractCustomerQueue(self):
        """extract the number of customer in the queue updated for each event occurrence"""
        temp = []
        for element in self.event_buffer:
            temp.append(element[1])
        return temp


class CustomerAverage(object):

    def __init__(self):
        self.total_area = 0.0
        self.old_sample = 0.0
        self.last_time = 0.0

    def update(self, current_time, current_sample):
        """implementation of the time average"""
        delta_time = float(current_time) - self.last_time
        self.total_area += self.old_sample * delta_time
        self.old_sample = current_sample
        self.last_time = current_time

    def mean(self, final_time):
        """computation of the mean"""
        return self.total_area/final_time
