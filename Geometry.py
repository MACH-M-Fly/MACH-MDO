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
			return ( A**2*y - A*(A-B)/(b_wing/4)*y**2 + (A - B)**2/(3*(b_wing/4)**2)*y**3)

		MAC = 0
		for i in range(0,4):
			MAC += 2.0/Sref_wing*(shape_func(Yle[i+1], C[i], C[i+1]) - shape_func(Yle[i], C[i], C[i+1]))
			# print(MAC)
	
		wing_edge = Xle + [sum(x) for x in zip(Xle, C)][::-1] + [sum(x) for x in zip(Xle, C)] + [1*x for x in Xle[::-1]]
		wing_pos = Yle + Yle[::-1] + [-1*x for x in Yle] + [-1*x for x in Yle[::-1]]

		tail_edge = Xle_t + [sum(x) for x in zip(Xle_t, C_t)][::-1] + [sum(x) for x in zip(Xle_t, C_t)] + [1*x for x in Xle_t[::-1]]
		tail_pos = Yle_t + Yle_t[::-1] + [-1*x for x in Yle_t] + [-1*x for x in Yle_t[::-1]]


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

# -- END OF FILE --		
					
