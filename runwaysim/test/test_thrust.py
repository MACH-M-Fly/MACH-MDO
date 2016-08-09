import matplotlib.pyplot as plt
import numpy as np




def thrust(vel, ang):
	T_0 = 12.756
	T_1 = -0.0941*3.28
	T_2 = 0.0023*3.28**2
	T_3 = -7*10**-5*3.28**3
	T_4 = 0 # 4*10**-7*3.28**4

	T = vel**4*T_4 + vel**3*T_3 + vel**2*T_2 + vel*T_1 + T_0
			#X comp   # Y Comp

	return (np.cos(ang)*T, np.sin(ang)*T )


vel = np.linspace(0, 50, 100)
ang = 0
T = [thrust(x, ang) for x in vel]


plt.plot(vel, T, 'b')
plt.show()