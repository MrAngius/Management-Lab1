import complex_queued_web_service as cws
import simplified_web_service as sw
import random


class WebAccelerator(cws.ComplexQueue, sw.Queue):
    def __init__(self, service_time_front, service_time_back, arrival_time_front, num_service_front,
                 number_service_back, environment, service_stats, customer_stats_front, customer_stats_back,
                 size_front, size_back, a, b, hit_cache):
        cws.ComplexQueue.__init__(self, service_time_front, arrival_time_front, num_service_front, environment,
                                  service_stats, customer_stats_front, size_front, a, b)
        self.hit_percentage = hit_cache
        self.back_queue = self.BackEndServer(service_time_back, number_service_back, environment, service_stats,
                                             customer_stats_back, size_back)
        self.count = 0

    def arrivals(self, packet=None):
        return cws.ComplexQueue.arrivals(self, packet)

    def endService(self, inter_service, packet):
        # STATISTICS
        self.customer_stats.eventRegistration(self.env.now, len(self.services.queue))
        packet.addTimeService(self.env.now)
        packet.computed_service = inter_service

        # have to establish if the packet can be served or not by the front-end
        rand = random.uniform(0, 1) * 100
        if rand > self.hit_percentage:
            self.back_queue.arrivals(packet=packet)
        else:
            self.service_stats.addPacket(packet)

    # inner class for modelling the back-end server
    class BackEndServer(cws.ComplexQueue):
        def __init__(self, service_time_back, num_service, environment, service_stats, customer_stats, size):
            cws.ComplexQueue.__init__(self, service_time_back, None, num_service, environment, service_stats,
                                      customer_stats, size, None, None)

        def arrivals(self, packet=None):
            # check if there's space in the queue
            if len(self.services.queue) < self.queue_size:
                self.callForService(None, self.env.now)
            else:
                self.dropPackets(None, self.env.now)
