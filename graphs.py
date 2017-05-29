from matplotlib import pyplot
import numpy


class Graphs(object):

    @staticmethod
    def meanAndConfidenceInterval(roh, means, lower_interval, upper_interval, y_label, title):
        pyplot.figure()

        pyplot.plot(roh, means, 'g')
        pyplot.xlabel('roh')
        pyplot.ylabel(y_label)
        pyplot.title(title)
        pyplot.grid(True)

        pyplot.fill_between(roh, lower_interval, upper_interval, color='#b9cfe7', edgecolor="")

    @staticmethod
    def customerQueueView(time, customers, y_label, title):
        pyplot.figure()

        pyplot.step(time, customers, 'g')
        pyplot.xlabel('time')
        pyplot.ylabel(y_label)
        pyplot.title(title)
        pyplot.grid(True)

    @staticmethod
    def showRk(rk):
        pyplot.figure()

        pyplot.plot(range(1, len(rk) + 1), rk, 'c')
        pyplot.xlabel('k')
        pyplot.ylabel('mean')
        pyplot.title('Rk relative variation')
        pyplot.grid(True)
        pyplot.hold(True)
        pyplot.plot(range(1, len(rk) + 1), [numpy.mean(rk)] * (len(rk)))
        pyplot.hold(False)

    @staticmethod
    def responseTimeShow(x, mean):
        pyplot.figure()

        pyplot.plot(range(1, len(x) + 1), x, 'r')
        pyplot.xlabel('time')
        pyplot.ylabel('response_time')
        pyplot.title('Response time variation')
        pyplot.grid(True)
        pyplot.hold(True)
        pyplot.plot(range(1, len(x) + 1), [mean] * (len(x)))
        pyplot.hold(False)

    @staticmethod
    def show():
        pyplot.show()
