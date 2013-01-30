import numpy
import pylab as p
#import matplotlib.axes3d as p3
import mpl_toolkits.mplot3d.axes3d as p3

# u and v are parametric variables.
# u is an array from 0 to 2*pi, with 100 elements
u = numpy.r_[0:2 * numpy.pi:100j]
# v is an array from 0 to 2*pi, with 100 elements
v = numpy.r_[0:2 * numpy.pi:100j]
# x, y, and z are the coordinates of the points for plotting
# each is arranged in a 100x100 array

a = 10
c = 20
x = numpy.outer((c + a * numpy.cos(v)), numpy.cos(u))
y = numpy.outer((c + a * numpy.cos(v)), numpy.sin(u))
z = numpy.outer((a * numpy.sin(v)), numpy.ones(numpy.size(u)))


fig = p.figure()
ax = p3.Axes3D(fig)
ax.plot_wireframe(x, y, z)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.grid(True)
p.show()
