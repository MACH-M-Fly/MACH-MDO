from matplotlib import pyplot
import numpy


a = numpy.arange(int(1e7))
# large so you can easily see the memory footprint on the system monitor.
fig = pyplot.Figure()
ax  = pyplot.plot(1, 1, 1)
lines = ax.plot(a) # this uses up an additional 230 Mb of memory.
# can I get the memory back?
l = lines[0]
l.remove()
del l
del lines
# not releasing memory
ax.cla()