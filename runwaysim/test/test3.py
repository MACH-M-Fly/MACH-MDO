from xfoil_lib import *
import matplotlib.pyplot as plt

name = 'E420_opt'
start = 3
end =  15

xfoil_run(name, 400000, start, end)

LtoD = getLtoD(name)
Cl = getCl(name)
Alpha = getAlpha(name)

# def f(t):
#     return np.exp(-t) * np.cos(2*np.pi*t)

# t1 = np.arange(0.0, 5.0, 0.1)
# t2 = np.arange(0.0, 5.0, 0.02)




plt.figure(1)
plt.subplot(211)
plt.ylabel('L/D')
plt.plot(Alpha,LtoD, 'ro')

plt.subplot(212)
plt.ylabel('Cl')
plt.xlabel('Alpha')
plt.plot(Alpha,Cl, 'bo')
plt.show()

