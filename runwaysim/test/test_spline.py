import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from spline import *

TE_gap = 0.001

x2 = 0.8
y2 = 0.05

x3 = 0.6
yt = 0.09

x4 = 0.5

x5 = 0.2

y6 = 0.04

y8 = -0.03

x9 = 0.2
yb = -0.04

x10 = 0.3

x11 = 0.4

x12 = 0.7
y12 = -0.007

x13 = 0.9
y13 = -0.01




cv = np.array([[ 1.0, TE_gap/2],
   [ x2,  y2],
   [ x3,  yt],
   [ x4,  yt],
   [ x5,  yt],
   [ 0.0, y6],
   [ 0.0, 0.0],
   [ 0.0, y8],
   [ x9,  yb],
   [ x10,  yb],
   [ x11,  yb],
   [ x12,  y12],
   [ x13,  y13],
   [ 1,  -TE_gap/2]])


points = bspline(cv)
# print(points)

plt.plot(points[:,0], points[:,1], 'b', cv[:,0], cv[:,1], 'ro--')
plt.ylim([-0.5,0.5])


plt.show()