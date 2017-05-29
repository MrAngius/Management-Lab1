import numpy
import math

from graphs import Graphs


class Statistics(object):
    """class used to evaluate statistics in our simulation"""

    def __init__(self):
        self.vector_time_arrival = []
        self.vector_time_service = []
        self.vector_time_service_back = []
        self.vector_packet_dropped = []
        self.packet_arrived = 0
        self.packet_served = 0
        self.avg_number_customer = CustomerAverage()
        self.avg_number_customer_back = CustomerAverage()
        self.warm_up_manager = WarmUpCut(0.0000001)

        self.customer_buffer_back = []

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

    def updateServiceBack(self, service_time, back_flag=False):
        """update the vector of service-time for back-end"""
        if not back_flag:
            self.vector_time_service_back.append(service_time)
        else:
            for k in range(len(self.vector_time_service_back)):
                if self.vector_time_service_back[k] == -1:
                    self.vector_time_service_back[k] = service_time
                    break

    def combineTimeOfService(self):
        temp = []
        zeros = []
        for front, back in zip(self.vector_time_service, self.vector_time_service_back):
            temp.append(front + back)
            zeros.append(0)
        self.vector_time_service = temp
        # we have to reset the already added times, in case of additions due to batch dynamic
        self.vector_time_service_back = zeros

    def updateAverageCustomers(self, current_time, waiting_customers, back_flag=False):
        """save for each event the time and the number of customers in the queue"""
        self.customer_buffer.append((current_time, waiting_customers))
        if back_flag:
            self.customer_buffer_back.append((current_time, waiting_customers))

    def computeAverageCustomers(self):
        """return the average of customers in the queue"""
        for data in self.customer_buffer:
            self.avg_number_customer.update(data[0], data[1])

        return self.avg_number_customer.mean(self.customer_buffer[-1][0])

    def computeAverageCustomersBack(self):
        """return the average of customers in the queue"""
        for data in self.customer_buffer_back:
            self.avg_number_customer_back.update(data[0], data[1])

        return self.avg_number_customer_back.mean(self.customer_buffer_back[-1][0])

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

    def extractCustomerTimeArrivalQueue(self):
        """extract the time at witch a new customer arrives in the queue"""
        temp = []
        for element in self.customer_buffer:
            temp.append(element[0])
        return temp

    def batchesResponseTime(self, numb_batches, warm_up=False, back_flag=False):
        """extract a list of batches for the response time from a long vector of samples"""
        if back_flag:
            self.combineTimeOfService()
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

    def batchesCustomerQueue(self, numb_batches, warm_up=False, back_flag=False):
        """extract a list of batches for the number of customer in the queue from a long vector of samples"""
        if not back_flag:
            customers = self.customer_buffer
        else:
            customers = self.customer_buffer_back

        if warm_up:
            worm_cut = WarmUpCut(0.000001, k=0)
            cut_customer_vector = worm_cut.eliminateWarmUpCustomer(customers)
            temp = zip(*[iter(cut_customer_vector)] * int(math.ceil(len(cut_customer_vector) / numb_batches)))
            if len(temp) > numb_batches:
                temp.pop()
                return temp
            return temp
        else:
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

    # TODO: implement an heuristic to remove the warm up for the response time
    def eliminateWarmUpResponseTime(self, vector_data):
        """iterate over the vector and compare the average in order to check for the steady state samples"""
        temp_vector = []
        rk = []
        x = numpy.mean(vector_data)

        while self.k <= len(vector_data) / 100:
            temp_vector = vector_data[self.k * 15:]
            temp_mean = numpy.mean(temp_vector)
            rk.append((temp_mean - x) / x)
            self.previous_mean = temp_mean
            self.k += 1

        Graphs.showRk(rk)
        Graphs.responseTimeShow(vector_data, x)
        Graphs.show()

        return temp_vector

    # TODO: implement an heuristic to remove the warm up for the customers
    def eliminateWarmUpCustomer(self, vector_data):
        """iterate over the vector and compare the average in order to check for the steady state samples"""
        temp_vector = []
        rk = []

        # mean computation for the customers in the queue
        customer_avg = CustomerAverage(vector_data[0][0])

        for data in vector_data:
            customer_avg.update(data[0], data[1])

        x = customer_avg.mean(vector_data[-1][0])

        while self.k < len(vector_data) / 100:
            temp_vector = vector_data[self.k * 15:]

            # mean computation for the customers in the queue
            customer_avg = CustomerAverage(temp_vector[0][0])

            for data in temp_vector:
                customer_avg.update(data[0], data[1])

            customer_mean = customer_avg.mean(list(temp_vector)[-1][0])

            rk.append(((customer_mean - x) / x))

            # DEBUG
            print str(((customer_mean - x) / x)) + " -- " + str(len(temp_vector)) + "/" + str(len(vector_data)) + "\n"
            print "\n" + str(self.k) + "/" + str(len(vector_data) / 100)

            self.previous_mean = customer_mean
            self.k += 1

        Graphs.showRk(rk)

        time = []
        cust = []
        for element in vector_data:
            time.append(element[0])
            cust.append(element[1])

        Graphs.customerQueueView(time, cust, "cust", "customer in queue")
        Graphs.show()

        return temp_vector
