# LAP TIME
from scipy.optimize import *
from sympy import Symbol, nsolve
import numpy as np
import matplotlib.pyplot as plt
import time as tim

from forces import *
from constants import *
from lib_runwaysim_damp import *

# Declare Consonstatns

def num_laps():

	max_time = 4*60
	N = 0
	leg_len = 500*0.3048
	Flapped = 0


	def calc_velcruise(weight):

		
		def sum_forces (A):

			vel = A[0]
			ang = A[1]


			F = np.empty(2)

			F[0] = thrust(vel, ang)[0] - 0.5*vel**2*Rho*CD(ang)*Sref_wing
			F[1] = gross_lift(vel, ang, Flapped) - weight

			return F




	 	Z = fsolve(sum_forces,np.array([25, 0*np.pi/180]))
		# print(CL(Z[1]))

	    # vel = np.linspace(-15, 15, 100)
		# ang = . #Z[1]
		# T = [thrust(x, ang)[0] for x in vel]
		# D = [ 0.5*x**2*Rho*CD(ang)*Sref_wing for x in vel]
		# L = [gross_lift(x, ang, Flapped) for x in vel]


		# vela =  10#Z[0]
		# ang = np.linspace(-np.pi/4, np.pi/4, 100)
		# Ta = [thrust(vela, x)[0] for x in ang]
		# Da = [ 0.5*vela**2*Rho*CD(x)*Sref_wing for x in ang]
		# La = [gross_lift(vela, x, Flapped) for x in ang]


		# plt.figure(1)
		# plt.subplot(211)
		# plt.ylabel('thrust / drag')
		# plt.xlabel('vel')
		# plt.plot(vel, T, 'b', vel, D, 'r', vel, L, 'g')

		# plt.subplot(212)
		# plt.ylabel('thrust / drag')
		# plt.xlabel('ang')
		# plt.plot(ang, Ta, 'b', ang, Da, 'r', ang , La, 'g')


	 	# print(fsolve(sum_forces,np.array([50, 0*np.pi/180])))
	 	# sum_forces(Z)

	 	ang = Z[1]
	 	vel =  Z[0]


	 	return (vel, ang)

	def calc_climb(weight):

		
		def sum_forces (A):

			vel = A[0]
			gamma = A[1]


			F = np.empty(2)

			F[0] = thrust(vel, ang)[0] - 0.5*vel**2*Rho*CD(ang)*Sref_wing - weight*np.sin(gamma)
			F[1] = gross_lift(vel, ang, Flapped ) - weight*np.cos(gamma)

			return F



		sol = np.empty((0,3), float)
		A = np.zeros((1,3))
		AoA = []

		for k in np.linspace(-7*np.pi/180, 7*np.pi/180, 30):

			ang = k

			AoA.append(ang)

			Z = fsolve(sum_forces,np.array([25, 10*np.pi/180]))

			A[0,0] = Z[0]
			A[0,1] = Z[1]
			A[0,2] = np.sin(Z[1])*Z[0]

			# print(A)

			sol
			# print(Z)


			sol = np.append(sol, A, axis=0)

		# AoA = [x * 180/np.pi for x in AoA]

		# fig, ax1 = plt.subplots()

		# ax1.plot(AoA, [x * 180/np.pi for x in sol[:,1]] , 'b')
		# ax1.set_xlabel('Angle of Attack [Deg])')
		# # Make the y-axis label and tick labels match the line color.
		# ax1.set_ylabel('Climb Angle [Deg]', color='b')
		# for tl in ax1.get_yticklabels():
		#     tl.set_color('b')

		# ax2 = ax1.twinx()
		# ax2.plot(AoA, sol[:,2], 'r')
		# ax2.set_ylabel('Climb Rate [m/s]', color='r')
		# for tl in ax2.get_yticklabels():
		#     tl.set_color('r')

		V_climb = np.max(sol[:,2])
		# print(np.where(sol[:,2] == V_climb))

		index = np.where(sol[:,2] == V_climb)[0][0]
		# print(index)

		AoA_climb = AoA[index]
		vel_climb = sol[index,0]

		# print(vel_climb)
		# print(V_climb)
		# print(AoA_climb)

		return(vel_climb, V_climb, AoA_climb)

	def cruise(dist, velocity):
		time = dist/velocity
		return time 

	def turn(bank_angle, velocity, weight , turn_angle):
		bank_angle_r = bank_angle*np.pi/180
		g = 9.81

		rad = velocity**2/(np.tan(bank_angle)*g)
		CL = (weight*2)/(np.cos(bank_angle_r)*Sref_wing*Rho*velocity**2)

		t = (rad*2*np.pi*(turn_angle/360))/velocity

		return t


	climb_vel, climb_rate, climb_AoA = calc_climb(weight)
	cruise_vel, cruise_AoA = calc_velcruise(weight)

	# print(cruise_vel)


	# ==========================  beign takeoff ===========================
	#find time to takeoff
	takeoff,dist, vel, ang, ang_vel, time =  runway_sim_damp(CL, CD, CM, CL_tail_noflap, CL_tail_flap)
	if takeoff == 0:
		return 0

	time = time + cruise(leg_len - dist, cruise_vel)
	time = time + turn(35, cruise_vel, weight, 180)
	time = time + cruise(leg_len, cruise_vel)
	time = time + turn(40, cruise_vel, weight, 360)
	time = time + cruise(leg_len, cruise_vel)
	time = time + turn(35, cruise_vel, weight, 180)
	time = time + cruise(leg_len, cruise_vel)

	while time < max_time:
		N = N + 1

		time = time + cruise(leg_len - dist, cruise_vel)
		time = time + turn(35, cruise_vel, weight, 180)
		time = time + cruise(leg_len, cruise_vel)
		time = time + turn(40, cruise_vel, weight, 360)
		time = time + cruise(leg_len, cruise_vel)
		time = time + turn(35, cruise_vel, weight, 180)
		time = time + cruise(leg_len, cruise_vel)



		
	return N




