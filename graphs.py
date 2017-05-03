from matplotlib import pyplot


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
