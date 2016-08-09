from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import time as tim


from forces import *
from constants import *
#


def runway_sim_damp(CL, CD, CM, CL_tail_noflap, CL_tail_flap):



	Flapped = 0

	#declare functions for kinimatic varibles (F = ma and M = I*ang_a)

	# super trivail func, but it helped me organize my thoughts
	def velocity(vel):
		return vel


	def acceleration(vel, ang):
		N =  weight - gross_lift(vel,ang, Flapped)
		if N < 0:
			N = 0
		accel = (g/weight)*(thrust(vel, ang)[0] - 0.5*vel**2*Rho*CD(ang)*Sref_wing - mu_k*N)
		return accel


	def ang_velocity(a_vel, ang):
		if (ang <= 0.0 and a_vel < 0.0) :
			#print('1')
			a = 0
		elif (ang >= max_rot_ang and a_vel > 0.0):
			#print('2')
			a = 0
		else:
			#print('3')
			a = a_vel

		return a


	def ang_acceleration(vel, ang, a_vel):

		moment_tail = - 0.5*Rho*vel**2*tail_CL(ang, Flapped)*Sref_tail*(boom_length - dist_landgear)
		moment_wing = 0.5*Rho*vel**2*(CM(ang)*Sref_wing*Cref+ CL(ang)*Sref_wing*dist_landgear)
		damping_moment =  -np.sign(a_vel)*0.5*Rho*a_vel**2*50*Sref_wing
		#print(damping_moment)
		ang_accel = 1.0/(I_G + (weight/g)*(dist_landgear)**2)*(moment_wing+moment_tail+damping_moment)
		#print(ang_accel)
		if (ang <= 0.0 and ang_accel < 0.0) :
			#print('1')
			ang_accel = 0
		elif (ang >= max_rot_ang and ang_accel > 0.0):
			#print('2')
			ang_accel = 0
		else:
			pass
			#print('3')


		return ang_accel



	# main loop

	dist = [0.0]
	vel = [0.0]
	ang = [0.0]
	ang_vel = [0.0]

	i = 0

	# accel = [acceleration(vel[i], ang[i ])]
	# ang_accel = [ ang_acceleration(vel[i], ang[i], ang_vel[i]) ]


	drag = [ 0.0 ]
	
	dt = 0.05
	time = [0.0]
	sum_y =  gross_lift(vel[i],ang[i], Flapped) - weight
	time_elap = 0
	# Y_sum = [sum_y]

	while (sum_y <= 0.0 and time_elap < 50) :

		# F = ma yeilds two second order equations => system of 4 first order
		# runge Kutta 4th to approximate kinimatic varibles at time = time + dt
		k1_dist = dt*velocity(vel[i])
		k1_vel = dt*acceleration(vel[i],ang[i])
		k1_ang = dt*ang_velocity(ang_vel[i], ang[i])
		k1_ang_vel = dt*ang_acceleration(vel[i], ang[i], ang_vel[i])

		k2_dist = dt*velocity(vel[i] + 0.5*k1_vel)
		k2_vel = dt*acceleration(vel[i] + 0.5*k1_vel, ang[i] + 0.5*k1_ang)
		k2_ang = dt*ang_velocity(ang_vel[i] + 0.5*k1_ang, ang[i] + 0.5*k1_ang)
		k2_ang_vel = dt*ang_acceleration(vel[i] + 0.5*k1_vel, ang[i] + 0.5*k1_ang, ang_vel[i] + 0.5*k1_ang_vel)

		k3_dist = dt*velocity(vel[i] + 0.5*k2_vel)
		k3_vel = dt*acceleration(vel[i] + 0.5*k2_vel, ang[i] + 0.5*k2_ang)
		k3_ang = dt*ang_velocity(ang_vel[i] + 0.5*k2_ang, ang[i] + 0.5*k2_ang)
		k3_ang_vel = dt*ang_acceleration(vel[i] + 0.5*k2_vel, ang[i] + 0.5*k2_ang, ang_vel[i] + 0.5*k2_ang_vel)

		k4_dist = dt*velocity(vel[i] +  k3_vel)
		k4_vel = dt*acceleration(vel[i] + k3_vel, ang[i] + k3_ang)
		k4_ang = dt*ang_velocity(ang_vel[i] + k3_ang, ang[i] + k3_ang)
		k4_ang_vel = dt*ang_acceleration(vel[i] + k3_vel, ang[i] + k3_ang, ang_vel[i] + k3_ang_vel)



		dist.append(dist[i] + 1.0/6*(k1_dist + 2*k2_dist + 2*k3_dist + k4_dist))
		vel.append(vel[i] + 1.0/6*(k1_vel + 2*k2_vel + 2*k3_vel + k4_vel))
		ang.append(ang[i] + 1.0/6*(k1_ang + 2*k2_ang + 2*k3_ang + k4_ang)) 
		ang_vel.append(ang_vel[i] + 1.0/6*(k1_ang_vel + 2*k2_ang_vel + 2*k3_ang_vel + k4_ang_vel))


		# accel.append(acceleration(vel[i + 1], ang[i + 1]))
		# ang_accel.append(ang_acceleration(vel[i + 1], ang[i+ 1], ang_vel[i+1]))
		# drag.append(- 0.5*vel[i +1]**2*Rho*CD(ang[i+1])*Sref_wing - mu_k*(weight - gross_lift(vel[i + 1],ang[ i + 1], Flapped)))
		time.append(time[i] + dt)

		# evaluate lift_net
		i = i + 1
		time_elap = time[i]
		#print(time_elap)
		sum_y =  gross_lift(vel[i],ang[i], Flapped) - weight
		# Y_sum.append(sum_y)


		if vel[i] > 10:
			Flapped = 1
		
		# print(i)
		# print(time[i])
		# print('sum forces y: ' +str(sum_y))
		# print("dist: "+str(dist[i]) + ' vel: ' +str(vel[i]) + ' ang: ' +str(ang[i]*180/3.1516) + ' ang vel: ' +str(ang_vel[i]))


	# #post process


	# #print((CL(4.0/180.0*3.1516)*Sref_wing + CL_tail(4.0/180.0*3.1516 - 12.20/180.0*3.1516)*Sref_tail)/(Sref_tail+Sref_wing))


	# print(time[i])
	# print("dist: "+str(dist[i]) + ' vel: ' +str(vel[i]) + ' ang: ' +str(ang[i]*180/3.1516) + ' ang vel: ' +str(ang_vel[i]))



	# ang = [x * 180/np.pi for x in ang]

	runway_len = 200 #meters

	if (dist[i] <= runway_len):
		takeoff = 1
	else:
		takeoff = 0

	# plt.figure(1)
	# plt.subplot(614)
	# plt.ylabel('distance')
	# plt.xlabel('time')
	# plt.plot(time, dist, 'b')


	# plt.subplot(611)
	# plt.ylabel('Angle)')
	# plt.xlabel('time')
	# plt.plot(time, ang, 'b')

	# plt.subplot(615)
	# plt.ylabel('Velocity')
	# plt.xlabel('time')
	# plt.plot(time, vel, 'b')



	# plt.subplot(612)
	# plt.ylabel('ang velocity')
	# plt.xlabel('time')
	# plt.plot(time, ang_vel, 'b')


	# plt.subplot(616)
	# plt.ylabel('acceleration')
	# plt.xlabel('time')
	# plt.plot(time, accel, 'b')

	# Thrust = []
	# for j in range(0, len(vel)):
	# 	# print(j)
	# 	Thrust.append(thrust(vel[j],ang[j])[0])



	# # plt.subplot(515)
	# # plt.ylabel('thrust')
	# # plt.xlabel('time')
	# # plt.plot(dist, Thrust,  'b')

	# plt.subplot(613)
	# plt.ylabel('ang acceleration')
	# plt.xlabel('time')
	# plt.plot(time, ang_accel, 'b')


	# # plt.plot(alphas, CLs, 'b', range(0,13), CL(range(0,13)), 'b--' )
	# #plt.show()
	# # # plt.ylabel('L/D')

	# # plt.figure(2)
	# # plt.plot(time, Y_sum)
	# # plt.ylabel('Sum Y')
	# # plt.xlabel('time')
	# plt.show()


	return (takeoff, dist[i], vel[i], ang[i], ang_vel[i], time[i])




# notes


# add function for elevator deflection
	# optimize function for elevator deflection (for MFLY)
# add cd of tail
# FIND actual I_G for M-8
	# Same for MX-1 































































































































































































































































































































































































































































































































































































































































































































