from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import time as tim


from AVL.avl_lib import *
from xfoil.xfoil_lib import xfoil_run_flap, getData_xfoil



def runway_sim():



	filename = './AVL/M-8_data.dat'

	alphas, CLs, CDs, CMs = getData_AVL(filename)[0:4]
	alphas_tail, CLs_tail_flap = getData_xfoil('xfoil/elev_data_flap.dat')[0:2]
	alphas_tail_noflap,CLs_tail_noflap = getData_xfoil('xfoil/elev_data.dat')[0:2]

	# convert to radians

	alphas = [x * np.pi/180 for x in alphas]
	alphas_tail = [x * np.pi/180 for x in alphas_tail]

	# get func for aero coeificent
	CL = np.poly1d(np.polyfit(alphas,CLs, 1))
	CM = np.poly1d(np.polyfit(alphas,CMs, 2))
	CD = np.poly1d(np.polyfit(alphas,CDs, 2))
	CL_tail_flap = np.poly1d(np.polyfit(alphas_tail,CLs_tail_flap, 2))
	CL_tail_noflap = np.poly1d(np.polyfit(alphas_tail_noflap,CLs_tail_noflap, 2))
	#declare varibles 

	Rho = 1.225; # make global
	Sref_wing = 1.301
	Sref_tail = 0.212
	Cref = 0.488
	weight = 180 #97.8609 # in newtons
	g = 9.81
	I_G = 2
	mu_k = 0.005
	max_rot_ang = 11.45*np.pi/180
	dist_landgear = 0.076708 
	boom_length = 0.8509
	inced_ang = -5.0 *np.pi/180.0
	Flapped = 0


	def thrust(vel, ang):
		T_0 = 12.756
		T_1 = -0.0941*3.28
		T_2 = 0.0023*3.28**2
		T_3 = -7*10**-5*3.28**3
		T_4 =  4*10**-7*3.28**4

		T = vel**4*T_4 + vel**3*T_3 + vel**2*T_2 + vel*T_1 + T_0
				#X comp   # Y Comp
		return (np.cos(ang)*T, np.sin(ang)*T )

	def tail_CL(ang, flapped):
		if (flapped):
			return CL_tail_flap(ang + inced_ang)
		else:
			return CL_tail_noflap(ang + inced_ang)



	def gross_lift(vel, ang):
		l_net = 0.5*Rho*vel**2*(CL(ang)*Sref_wing + tail_CL(ang, Flapped)*Sref_tail)

		net_F = l_net + thrust(vel,ang)[1]

		return net_F

	#declare functions for kinimatic varibles (F = ma and M = I*ang_a)

	# super trivail func, but it helped me organize my thoughts

	def velocity(vel):
		return vel


	def acceleration(vel, ang):
		N =  weight - gross_lift(vel,ang)
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


	def ang_acceleration(vel, ang):

		ang_accel = (1.0/(I_G + (weight/g)*(dist_landgear)**2))*(0.5*Rho*vel**2*(CM(ang)*Sref_wing*Cref+ CL(ang)*Sref_wing*dist_landgear - tail_CL(ang, Flapped)*Sref_tail*(boom_length - dist_landgear)))

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

	accel = [acceleration(vel[i], ang[i ])]

	ang_accel = [ang_acceleration(vel[i], ang[i])]

	drag = [ 0.0 ]

	
	dt = 0.01
	time = [0.0]
	sum_y =  gross_lift(vel[i],ang[i]) - weight
	time_elap = 0
	Y_sum = [sum_y]

	while (sum_y <= 0.0 and time_elap < 50) :

		# F = ma yeilds two second order equations => system of 4 first order
		# runge Kutta 4th to approximate kinimatic varibles at time = time + dt
		k1_dist = dt*velocity(vel[i])
		k1_vel = dt*acceleration(vel[i],ang[i])
		k1_ang = dt*ang_velocity(ang_vel[i], ang[i])
		k1_ang_vel = dt*ang_acceleration(vel[i], ang[i])

		k2_dist = dt*velocity(vel[i] + 0.5*k1_vel)
		k2_vel = dt*acceleration(vel[i] + 0.5*k1_vel, ang[i] + 0.5*k1_ang)
		k2_ang = dt*ang_velocity(ang_vel[i] + 0.5*k1_ang, ang[i] + 0.5*k1_ang)
		k2_ang_vel = dt*ang_acceleration(vel[i] + 0.5*k1_vel, ang[i] + 0.5*k1_ang)

		k3_dist = dt*velocity(vel[i] + 0.5*k2_vel)
		k3_vel = dt*acceleration(vel[i] + 0.5*k2_vel, ang[i] + 0.5*k2_ang)
		k3_ang = dt*ang_velocity(ang_vel[i] + 0.5*k2_ang, ang[i] + 0.5*k2_ang)
		k3_ang_vel = dt*ang_acceleration(vel[i] + 0.5*k2_vel, ang[i] + 0.5*k2_ang)

		k4_dist = dt*velocity(vel[i] +  k3_vel)
		k4_vel = dt*acceleration(vel[i] + k3_vel, ang[i] + k3_ang)
		k4_ang = dt*ang_velocity(ang_vel[i] + k3_ang, ang[i] + k3_ang)
		k4_ang_vel = dt*ang_acceleration(vel[i] + k3_vel, ang[i] + k3_ang)



		dist.append(dist[i] + 1.0/6*(k1_dist + 2*k2_dist + 2*k3_dist + k4_dist))
		vel.append(vel[i] + 1.0/6*(k1_vel + 2*k2_vel + 2*k3_vel + k4_vel))
		ang.append(ang[i] + 1.0/6*(k1_ang + 2*k2_ang + 2*k3_ang + k4_ang)) 
		ang_vel.append(ang_vel[i] + 1.0/6*(k1_ang_vel + 2*k2_ang_vel + 2*k3_ang_vel + k4_ang_vel))


		# if ang[i + 1] < 0.0:
		# 	ang[i + 1 ] = 0.0
		


		accel.append(acceleration(vel[i + 1], ang[i + 1]))
		ang_accel.append(ang_acceleration(vel[i + 1], ang[i+ 1]))
		drag.append(- 0.5*vel[i +1]**2*Rho*CD(ang[i+1])*Sref_wing - mu_k*(weight - gross_lift(vel[i + 1],ang[ i + 1])))
		time.append(time[i] + dt)

		# evaluate lift_net
		i = i + 1
		time_elap = time[i]
		#print(time_elap)
		sum_y =  gross_lift(vel[i],ang[i]) - weight
		Y_sum.append(sum_y)


		if vel[i] > 10:
			Flapped = 1

		#print(ang_accel[i] < 0.0 )
	
		#tim.sleep(0.25)

		# print(i)
		# print(time[i])
		# print('sum forces y: ' +str(sum_y))
		# print("dist: "+str(dist[i]) + ' vel: ' +str(vel[i]) + ' ang: ' +str(ang[i]*180/3.1516) + ' ang vel: ' +str(ang_vel[i]))
		# print(CL_tail(ang[i]-20.0/180.0*3.1516))
		#print(str(k1_ang_vel) + ' ' + str(k2_ang_vel) + ' ' + str(k3_ang_vel) + ' ' + str(k4_ang_vel))
		# print((1.0/(I_G + (weight/g)*(dist_landgear)**2))*(0.5*Rho*vel[i]**2*(CM(ang[i])*Sref_wing*Cref+ CL(ang[i])*Sref_wing*dist_landgear + CL_tail(0)*Sref_tail*(boom_length - dist_landgear)))
#)


	#post process
	#print((CL(4.0/180.0*3.1516)*Sref_wing + CL_tail(4.0/180.0*3.1516 - 12.20/180.0*3.1516)*Sref_tail)/(Sref_tail+Sref_wing))
	print(time[i])
	print("dist: "+str(dist[i]) + ' vel: ' +str(vel[i]) + ' ang: ' +str(ang[i]*180/3.1516) + ' ang vel: ' +str(ang_vel[i]))

	ang = [x * 180/np.pi for x in ang]


	plt.figure(1)
	plt.subplot(614)
	plt.ylabel('distance')
	plt.xlabel('time')
	plt.plot(time, dist, 'r--')


	plt.subplot(611)
	plt.ylabel('Angle)')
	plt.xlabel('time')
	plt.plot(time, ang, 'r--')

	plt.subplot(615)
	plt.ylabel('Velocity')
	plt.xlabel('time')
	plt.plot(time, vel, 'r--')



	plt.subplot(612)
	plt.ylabel('ang velocity')
	plt.xlabel('time')
	plt.plot(time, ang_vel, 'r--')


	plt.subplot(616)
	plt.ylabel('acceleration')
	plt.xlabel('time')
	plt.plot(time, accel, 'r--')

	Thrust = []
	for j in range(0, len(vel)):
		# print(j)
		Thrust.append(thrust(vel[j],ang[j])[0])



	# plt.subplot(515)
	# plt.ylabel('thrust')
	# plt.xlabel('time')
	# plt.plot(dist, Thrust,  'r--')

	plt.subplot(613)
	plt.ylabel('ang acceleration')
	plt.xlabel('time')
	plt.plot(time, ang_accel, 'r--')


	# plt.plot(alphas, CLs, 'r--', range(0,13), CL(range(0,13)), 'b--' )
	#plt.show()
	# # plt.ylabel('L/D')

	plt.figure(2)
	plt.plot(time, Y_sum)
	plt.ylabel('Sum Y')
	plt.xlabel('time')
	plt.show()


	return (dist, vel, ang, ang_vel, time)




# notes

# add flap deflecion cl stuff
# add function for elevator deflection
	# optimize function for elevator deflection (for MFLY)
# add cd stuff for tail
# FIND actual I_G for M-8
	# Same for MX-1 































































































































































































































































































































































































































































































































































































































































































































