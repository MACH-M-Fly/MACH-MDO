from __future__ import division

from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder

from scipy.optimize import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os

import math

from gen_files import *


class mass_prop(Component):
	def __init__(self ): 
		super(mass_prop,self).__init__()

		self.add_param('b_wing',val=3.33)

		self.add_param('C_r',val=0.4)
		self.add_param('t2',val=0.4)
		self.add_param('t3',val=0.4)
		self.add_param('t4',val=0.4)
		self.add_param('t5',val=0.4)

		self.add_param('b_htail', val=1.0)
		self.add_param('C_r_t',val=0.4)

		self.add_param('boom_len', val=0.6)	
		self.add_param('dist_LG', val=0.15)

			
		# set up outputs
		self.add_output('mass', val= 3.0)
		self.add_output('x_cg', val = 0.0)
		self.add_output('z_cg', val = 0.0)					
		self.add_output('Iyy', val = 0.0)
		self.add_output('Sref_wing',val=2.0)
		self.add_output('Sref_tail', val=2.0)
		self.add_output('MAC',val=0.4)



		self.add_output('Xle', val=[]*5)
		self.add_output('Yle', val=[]*5)	  
		self.add_output('C', val=[]*5)	  
		self.add_output('Xle_t', val=[]*2)
		self.add_output('Yle_t', val=[]*2)
		self.add_output('C_t', val=[]*2)	 

	def solve_nonlinear(self,params,unknowns,resids):
		# make all input variables local for ease
		boom_len = params['boom_len']
		dist_LG = params['dist_LG']

		C = [params['C_r'], params['C_r']*params['t2'], params['C_r']*params['t2']*params['t3'], params['C_r']*params['t2']*params['t3']*params['t4'],  params['C_r']*params['t2']*params['t3']*params['t4']*params['t5']]
		b_wing = params['b_wing']


		Xle =  [0]
		for i in range(0, len(C)-1):
			Xle.append((C[i] - C[i +1])/4 + Xle[i])
			
		Yle =  [0, 1*b_wing/8,  b_wing/4, 3*b_wing/8, b_wing/2]
		Sref_wing = b_wing/8*(C[0] + 2*C[1] + 2*C[2] + 2*C[3] + C[4])

		b_htail = params['b_htail']
		Xle_t =[boom_len + C[0]/4.0, boom_len + C[0]/4.0]
		Yle_t = [0, b_htail/2.0]
		C_t = [params['C_r_t'] , params['C_r_t']]


		CDp = 0.0116


		def shape_func(y,A,B):
			# print('yes')
			return ( A**2*y - A*(A-B)/(b_wing/4)*y**2 + (A - B)**2/(3*(b_wing/4)**2)*y**3)

		MAC = 0
		for i in range(0,4):
			MAC += 2.0/Sref_wing*(shape_func(Yle[i+1], C[i], C[i+1]) - shape_func(Yle[i], C[i], C[i+1]))
			# print(MAC)
	

		#calc mass of the Wing
		rib_dens = 10  # ribs/ meter
		rib_dens_t = 10 

		linden_LE = 0.12 # kg/m
		linden_TE = 0.04 
		linden_spar = 0.35 #kg/m
		k_ribs = 0.0065 # kg

		linden_LE_t = 0.075
		linden_spar_t = 0.25
		k_ribs_t = 0.0045 #kg


		linden_boom = 0.107 #kg/m
		m_motor = 0.5
		m_battery = 0.617
		m_prop = 0.0181
		m_electronics = 0.2

		m_payload = 2.26796

		b_vtail = 0.463

		###############################################
		num_ribs = math.ceil(b_wing*rib_dens)
		m_ribs = k_ribs*num_ribs*(MAC/0.5)
		m_LE = linden_LE *b_wing
		m_TE = linden_TE *b_wing
		m_spar = linden_spar * b_wing

		m_wing = m_ribs + m_LE + m_TE + m_spar

		#calc mass of the tail
		num_ribs_t = math.ceil((b_htail+b_vtail)*rib_dens_t) 
		m_ribs_t = k_ribs_t*num_ribs_t
		m_LE_t = linden_LE *(b_htail+b_vtail)
		m_TE_t = linden_TE *(b_htail+b_vtail)
		m_spar_t = linden_spar_t * (b_htail+b_vtail)

		m_tail = m_ribs_t + m_LE_t + m_TE_t + m_spar_t

		#mass boom
		m_boom = boom_len*linden_boom 

		#mass landing gear
		height_LG = np.sin(10*np.pi/180)*(boom_len - dist_LG)
		m_landgear_rear = 0.69*height_LG*2
		m_landgear = m_landgear_rear + 0.163

		## total mass

		m_total = m_wing + m_tail + m_landgear + m_boom + m_motor+ m_battery + m_electronics + m_payload

	
		#########
		m_x = m_wing*0.25*MAC + m_landgear*dist_LG + m_tail*boom_len + m_boom*boom_len/2

		def x_CG_loc(mount_len):

			cg = (m_x + mount_len*m_motor + mount_len/2*m_battery )/m_total

			return (cg - MAC/4)

		#adjust the motor mount length until the CG is at c/4
		mount_len = fsolve(x_CG_loc,np.array([1]))[0]


		Iyy = (m_motor+m_prop)*mount_len**2 + m_battery*(mount_len/2)**2 + m_landgear*dist_LG**2 + m_tail*boom_len**2 + 1/3*m_boom*boom_len**2
		Ixx = 1/12*(m_wing*b_wing**2 + m_tail*b_htail**2)
		Izz = Ixx + Iyy

		x_cg = MAC/4
		z_cg = 0


		unknowns['Iyy'] = Iyy
		unknowns['x_cg'] = x_cg
		unknowns['z_cg'] = z_cg
		unknowns['Sref_wing'] = Sref_wing
		unknowns['Sref_tail'] = C_t[0]*b_htail
		unknowns['MAC'] = MAC
		unknowns['mass'] = m_total

		unknowns['Xle'] = Xle
		unknowns['Yle'] = Yle
		unknowns['C'] = C

		unknowns['Xle_t'] = Xle_t
		unknowns['Yle_t'] = Yle_t
		unknowns['C_t'] = C_t




		print('============== input =================')
		print('b_wing= ' + str(b_wing))
		print('C= ' + str(C))
		# print('b_htail= ' + str(b_htail))
		# print('C_t= ' + str(C_t))		
		# print('dist_LG= ' + str(dist_LG))
		# print('boom_len= ' + str(boom_len))
		# print(' ')

		# print('============== output =================')
		# print('Sref_wing: ' + str(Sref_wing))
		# print('Mount length: ' + str(mount_len))
		# print('MAC: ' + str(MAC))
		# print('Xle: ' + str(Xle))
		# print('x_cg: ' + str(x_cg) + '  z_cg: ' + str(z_cg))
		# print('Total Mass: ' +str(m_total))

		gen_mass( m_total, [x_cg, 0, z_cg], [Ixx, Iyy, Izz, 0, 0, 0])
		gen_geo(Sref_wing, MAC, b_wing, [x_cg, 0, z_cg], CDp, Xle, Yle, C, Xle_t, Yle_t, C_t)
	

		# ========================== PLOT ===============================
		wing_edge = Xle + [sum(x) for x in zip(Xle, C)][::-1] + [sum(x) for x in zip(Xle, C)] + [1*x for x in Xle[::-1]]
		wing_pos = Yle + Yle[::-1] + [-1*x for x in Yle] + [-1*x for x in Yle[::-1]]

		tail_edge = Xle_t + [sum(x) for x in zip(Xle_t, C_t)][::-1] + [sum(x) for x in zip(Xle_t, C_t)] + [1*x for x in Xle_t[::-1]]
		tail_pos = Yle_t + Yle_t[::-1] + [-1*x for x in Yle_t] + [-1*x for x in Yle_t[::-1]]



# -- END OF FILE --		
					
