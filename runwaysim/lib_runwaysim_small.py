from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

# from forces import thrust, tail_CL, gross_lift, g, mu_k, Sref_tail, Rho, inced_ang

Rho = 1.225 # make global
Sref_tail = 0.212
g = 9.81
mu_k = 0.005

inced_ang = -5.0 *np.pi/180.0
max_rot_ang = 10*np.pi/180.0

def runway_sim_small(CL, CD, CM, CL_tail_noflap, CL_tail_flap, Sref_wing, weight, boom_len, dist_LG, Cref, I_G):


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

	Flapped = 0

	#declare functions for kinimatic varibles (F = ma and M = I*ang_a)
	# super trivail func, but it helped me organize my thoughts
	def velocity(vel):
		return vel

	def acceleration(vel, ang):
		N =  weight - gross_lift(vel,ang, Sref_wing, Flapped)
		if N < 0:
			N = 0
		accel = (g/weight)*(thrust(vel, ang)[0] - 0.5*vel**2*Rho*CD(ang)*Sref_wing - mu_k*N)
		return accel

	def ang_velocity(a_vel, ang):
		if (ang <= 0.0 and a_vel < 0.0) :
			a = 0
		elif (ang >= max_rot_ang and a_vel > 0.0):
			a = 0
		else:
			a = a_vel


		return a

	def ang_acceleration(vel, ang, v_ang):
		q = 0.5*Rho*vel**2
		moment_tail = - q*tail_CL(ang, Flapped)*Sref_tail*(boom_len - dist_LG)
		moment_wing = q*(CM(ang)*Sref_wing*Cref+ CL(ang)*Sref_wing*dist_LG)
		# damping_moment =  -np.sign(a_vel)*0.5*Rho*a_vel**2*50*Sref_wing
		ang_accel = 1.0/(I_G + (weight/g)*dist_LG**2)*(moment_wing+moment_tail) # +damping_moment)
		
		if (ang <= 0.0 and ang_accel < 0.0) :
			ang_accel = 0
		elif (ang >= max_rot_ang and v_ang >= 0.0):
			ang_accel = -30*v_ang
			if (abs(ang_accel) < 10**-27 and Flapped):
				ang_accel = 0



		else:

			pass

		return ang_accel

	# main loop
	i = 0

	dist = [0.0]
	vel = [0.0]
	ang = [0.0]
	ang_vel = [0.0]

	accel = [acceleration(vel[i], ang[i ])]
	ang_accel = [ ang_acceleration(vel[i], ang[i], ang_vel[i]) ]


	v_stall = np.sqrt(2*weight/(Rho*Sref_wing*1.7))

	K1_ang_vel = [0.0]
	K2_ang_vel = [0.0]
	K3_ang_vel = [0.0]
	K4_ang_vel = [0.0]


	time = [0.0]
	dt = 0.5
	time_elap = 0

	DT =[dt]

	sum_y =  gross_lift(vel[i],ang[i], Sref_wing, Flapped) - weight

	while (sum_y <= 0.0 and time_elap < 20) :



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
		accel.append(acceleration(vel[i + 1], ang[i + 1]))
		ang_accel.append(ang_acceleration(vel[i + 1], ang[i+ 1], ang_vel[i+1]))

		K1_ang_vel.append(k1_ang_vel)
		K2_ang_vel.append(k2_ang_vel)
		K3_ang_vel.append(k3_ang_vel)
		K4_ang_vel.append(k4_ang_vel)

		i = i + 1

		if abs(ang_vel[i])< 10**-8 and Flapped:
			ang_vel[i] = 0.0

		# if ((vel[i] > 0.8*(v_stall+1.0)) and time[i- 1] < 7.0) :
		if not(not(vel[i] > 0.93*(v_stall+1.0)) or (abs(ang_accel[i]) < 10**-35 and Flapped)) :
			dt = 0.035
		else:
			dt = 0.5
		DT.append(dt)

		# if not(not(vel[i] > 0.95*(v_stall+1.0)) or (abs(ang_accel[i]) < 1**-40 and np.sign(ang_accel[i]) < 0.0 )) : #and ang_vel[i] == ang_vel[i -1] and (ang_accel > 0.0)) : #and vel
		# 	dt = 0.015
		# else:
		# 	dt = 0.05
		# print(ang_vel[i], ang_accel[i])




		time.append(time[i -1] + dt)


		time_elap = time[i]
		sum_y =  gross_lift(vel[i],ang[i], Sref_wing, Flapped) - weight

		# print( ang[i])

		if vel[i] > v_stall+1.0:
			Flapped = 1
		

	runway_len = 200 #meters

	if (dist[i] <= runway_len):
		takeoff = 1
	else:
		takeoff = 0




	# ang = [x * 180/np.pi for x in ang]

	# runway_len = 200 #meters

	# if (dist[i] <= runway_len):
	# 	takeoff = 1
	# else:
	# 	takeoff = 0

	# plt.figure(1)
	# plt.subplot(714)
	# plt.ylabel('distance')
	# plt.xlabel('time')
	# plt.plot(time, dist, 'b')


	# plt.subplot(711)
	# plt.ylabel('Angle)')
	# plt.xlabel('time')
	# plt.plot(time, ang, 'b')

	# plt.subplot(715)
	# plt.ylabel('Velocity')
	# plt.xlabel('time')
	# plt.plot(time, vel, 'b')



	# plt.subplot(712)
	# plt.ylabel('ang velocity')
	# plt.xlabel('time')
	# plt.plot(time, ang_vel, 'b')


	# plt.subplot(716)
	# plt.ylabel('K_ang_vel')
	# plt.xlabel('time')
	# plt.plot(time, K1_ang_vel, 'b', time, K2_ang_vel, 'r', time, K3_ang_vel, 'g', time, K4_ang_vel, 'k')#, time, K3_ang_vel, accel, 'g',time, K4_ang_vel, accel, 'y')

	# # Thrust = []
	# # for j in range(0, len(vel)):
	# # 	# print(j)
	# # 	Thrust.append(thrust(vel[j],ang[j])[0])



	# # # plt.subplot(515)
	# # # plt.ylabel('thrust')
	# # # plt.xlabel('time')
	# # # plt.plot(dist, Thrust,  'b')

	# plt.subplot(713)
	# plt.ylabel('ang acceleration')
	# plt.xlabel('time')
	# plt.plot(time, ang_accel, 'b')


	# plt.subplot(717)
	# plt.ylabel('dt')
	# plt.xlabel('time')
	# plt.plot(time, DT, 'b')


	# # # plt.plot(alphas, CLs, 'b', range(0,13), CL(range(0,13)), 'b--' )
	# # #plt.show()
	# # # # plt.ylabel('L/D')
	# print(len(time))
	# # # plt.figure(2)
	# # # plt.plot(time, Y_sum)
	# # # plt.ylabel('Sum Y')
	# # # plt.xlabel('time')
	plt.show()


	
	print('Takeoff:' + str(takeoff))
	print('Distance: ' + str(dist[i]))
	print('vel: ' + str(vel[i]))
	print('ang: ' + str(ang[i]*180.0/np.pi) + ' max_rot_ang: ' + str(max_rot_ang*180.0/np.pi))
	print('ang_vel: ' + str(ang_vel[i]))
	print('time: ' + str(time[i]))
	print(len(time))
	print('\n')

	return (takeoff, dist[i], vel[i], ang[i], ang_vel[i], time[i])































































































































































































































































































































































































































































































































































































































































































































