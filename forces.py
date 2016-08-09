import numpy as np
from constants_t import *
from AVL.avl_lib import *
from xfoil.xfoil_lib import xfoil_run_flap, getData_xfoil
import matplotlib.pyplot as plt


# from constants_t import *

Rho = 1.225 # make global
Sref_tail = 0.212
g = 9.81
mu_k = 0.005

inced_ang = -5.0 *np.pi/180.0

def get_aeroCoef(filename = 'aircraft_data.dat'):
	xfoil_path = '/home/josh/Documents/Research/MACHMDO/runwaysim/xfoil/elev_data'

	alphas, CLs, CDs, CMs = getData_AVL(filename)[0:4]
	alphas_tail, CLs_tail_flap = getData_xfoil(xfoil_path+ '_flap.dat')[0:2]
	alphas_tail_noflap,CLs_tail_noflap = getData_xfoil(xfoil_path+ '.dat')[0:2]

	# convert to radians

	
	# plt.figure(3)
	# plt.subplot(311)
	# plt.ylabel('CL')
	# plt.xlabel('Alpha')
	# plt.plot(alphas, CLs, 'b')

	# plt.subplot(312)
	# plt.ylabel('CD')
	# plt.xlabel('Alpha')
	# plt.plot(alphas, CDs, 'b')


	# plt.subplot(313)
	# plt.ylabel('CM')
	# plt.xlabel('Alpha')
	# plt.plot(alphas, CMs, 'b')


	# plt.subplot(714)
	# plt.ylabel('CL')
	# plt.xlabel('Alpha')
	# plt.plot(alphas_tail, Cls, 'b')



	alphas = [x * np.pi/180 for x in alphas]
	alphas_tail = [x * np.pi/180 for x in alphas_tail]



	# get func for aero coeificent
	CL = np.poly1d(np.polyfit(alphas,CLs, 1))
	CD = np.poly1d(np.polyfit(alphas,CDs, 2))
	CM = np.poly1d(np.polyfit(alphas,CMs, 2))

	CL_tail_flap = np.poly1d(np.polyfit(alphas_tail,CLs_tail_flap, 2))
	CL_tail_noflap = np.poly1d(np.polyfit(alphas_tail_noflap,CLs_tail_noflap, 2))

	return (CL, CD, CM, CL_tail_flap, CL_tail_noflap )


def thrust(vel, ang):
	T_0 = 12.756
	T_1 = -0.0941*3.28
	T_2 = 0.0023*3.28**2
	T_3 = -7*10**-5*3.28**3
	T_4 = 0 # 4*10**-7*3.28**4

	T = vel**4*T_4 + vel**3*T_3 + vel**2*T_2 + vel*T_1 + T_0
			#X comp   # Y Comp
	return (np.cos(ang)*T, np.sin(ang)*T )

def tail_CL(ang, flapped):
	if (flapped):
		return CL_tail_flap(ang + inced_ang)
	else:
		return CL_tail_noflap(ang + inced_ang)

def gross_lift(vel, ang, Sref_wing, flapped):
	l_net = 0.5*Rho*vel**2*(CL(ang)*Sref_wing + tail_CL(ang, flapped)*Sref_tail)

	gross_F = l_net + thrust(vel,ang)[1]

	return gross_F
