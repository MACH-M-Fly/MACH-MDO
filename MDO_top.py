#python stantdard libraries 
from __future__ import print_function
from time import localtime, strftime, time

# addition python libraries 
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

#open MDAO libraries
from openmdao.api import IndepVarComp, Component, Problem, Group
from openmdao.api import ScipyOptimizer, ExecComp, SqliteRecorder
from openmdao.drivers.pyoptsparse_driver import pyOptSparseDriver

#user defined libraries
from PostProcess import post_process
from weight import weight
from obj import obj
from lib_plot import *

FFMpegWriter = animation.writers['ffmpeg']
metadata = dict(title='MACH MDO', artist='MACH',comment='MDO Animation') 
writer = FFMpegWriter(fps=15, metadata=metadata)

class Constrained_MDO(Group):

	def __init__(self):
		super(Constrained_MDO,self).__init__()


	    #                     		  --------------
	    #                     		  |            |
	    #                     		  |		       |
	    #                     		  --------------
	    #                      		        |                                                       
	    #                                   |                                                         
	    #                                   |                                        
	    #                                   |                                                    
	    #                                   |                                                       
	    #                             ------|------
	    #                -------------	           -------------
	    #       --------					| 	   |	   |     ---------
	    #   ---							    					     |    ---
	    #  |								|	   |	   |		          |
	    #  								    					     |
	  	#  |								|	   |	   |			      |
	  	#  								    				         | 
	  	#  |								|	   |	   |	        	  |
	    #   -------  					    						 | -------
	    #          -----------              |      |       | ---------
	    #                     ------------------------------
		# 									1      2       3         4        5


		# ====================================== Params =============================================== #

		self.add('b_wing',IndepVarComp('b_wing',2.5)) 		# Wing Span 
		self.add('C_r',IndepVarComp('C_r',0.603))			# Root Airfoil Cord
		self.add('t2',IndepVarComp('t2',0.9506))  			# Taper ratio at 2
		self.add('t3',IndepVarComp('t3',0.9517))			# Taper ratio at 3 
		self.add('t4',IndepVarComp('t4',0.9558))			# Taper ratio at 4
		self.add('t5',IndepVarComp('t5',0.8117))			# Taper ratio at 5
		self.add('dist_LG',IndepVarComp('dist_LG',0.07))	# Distance between the CG and the Landing Gear 
		self.add('b_htail',IndepVarComp('b_htail',1.0))		# Horizontail Tail Span 
		self.add('C_r_t',IndepVarComp('C_r_t',0.228))		# Tail Root airfoil Cord 
		# self.add('b_vtail',IndepVarComp('b_vtail',0.3))	# Vertical Tail Span
		self.add('boom_len',IndepVarComp('boom_len',0.5))	# Boom Length
																		#[ 1     2     3     4     5  ]
		self.add('camber',        IndepVarComp('camber',        np.array([0.13, 0.13, 0.13, 0.13, 0.13])))  # Camber % at each position 
		self.add('max_camb_pos',  IndepVarComp('max_camb_pos',  np.array([0.45, 0.45, 0.45, 0.45, 0.45]))) 	# Max Camber Position % at each position
		self.add('thickness',     IndepVarComp('thickness',     np.array([0.14, 0.14, 0.14, 0.14, 0.14]))) 	# Thickness % at each position 
		self.add('max_thick_pos', IndepVarComp('max_thick_pos', np.array([0.29, 0.29, 0.29, 0.29, 0.29]))) 	# Max Thickness Postion % at each position

		# Add Componets 

		self.add('weight', weight())   

		self.add('obj', obj())
		self.add('Plot', Plot(geo1, geo2, A, writer, fig))
  
		# ====================================== Connections ============================================ # 

		self.connect('b_wing.b_wing',['weight.b_wing','obj.b_wing'])

		self.connect('C_r.C_r',['weight.C_r'])
		self.connect('t2.t2',['weight.t2'])
		self.connect('t3.t3',['weight.t3'])
		self.connect('t4.t4',['weight.t4'])
		self.connect('t5.t5',['weight.t5'])

		self.connect('b_htail.b_htail',['weight.b_htail'])
		self.connect('C_r_t.C_r_t',['weight.C_r_t'])


		self.connect('dist_LG.dist_LG',['weight.dist_LG','obj.dist_LG'])
		self.connect('boom_len.boom_len',['weight.boom_len','obj.boom_len'])

		self.connect('camber.camber', ['obj.camber'])
		self.connect('max_camb_pos.max_camb_pos',['obj.max_camb_pos'])
		self.connect('thickness.thickness', ['obj.thickness'])
		self.connect('max_thick_pos.max_thick_pos', ['obj.max_thick_pos'])


		# Connections weight Module
		self.connect('weight.mass', 'obj.mass')					
		self.connect('weight.Iyy', 'obj.Iyy')
		self.connect('weight.Sref_wing' , 'obj.Sref_wing')
		self.connect('weight.Sref_tail' , 'obj.Sref_tail')
		self.connect('weight.MAC', 'obj.MAC')
		self.connect('weight.x_cg', ['obj.x_cg', 'Plot.x_cg'])
		self.connect('weight.Xle', 'Plot.Xle')
		self.connect('weight.Yle', 'Plot.Yle')
		self.connect('weight.C', 'Plot.C')
		self.connect('weight.Xle_t', 'Plot.Xle_t')
		self.connect('weight.Yle_t', 'Plot.Yle_t')
		self.connect('weight.C_t', 'Plot.C_t')

		# Connections obj Module
		self.connect('obj.NP', 'Plot.NP')					
		self.connect('obj.score','Plot.score')


		# self.add('OBJ_cmp', ExecComp('OBJ = obj.score'), promotes=['*'])
		
# ==================================== Initailize plots for animation ===================================== #

fig = plt.figure(figsize=[12,8])

geo1 = plt.subplot2grid((5, 5), (0, 0), colspan=3, rowspan=4)
geo2 = plt.subplot2grid((5, 5), (4, 0), colspan=3, rowspan=1)
geo1.set_xlim([-2, 2])
geo1.set_ylim([-0.5, 2])
geo2.set_xlim([-2, 2])
geo2.set_ylim([-0.5,0.5])

A = []
A.append(plt.subplot2grid((5, 5), ( 0, 3), colspan=2))
A.append(plt.subplot2grid((5, 5), ( 1, 3), colspan=2))
A.append(plt.subplot2grid((5, 5), ( 2, 3), colspan=2))
A.append(plt.subplot2grid((5, 5), ( 3, 3), colspan=2))
A.append(plt.subplot2grid((5, 5), ( 4, 3), colspan=2))
for i in range(0,5):
	A[i].set_xlim([0, 0.7])
	A[i].set_ylim([-0.1, 0.2])

plt.tight_layout()

# ============================================== Create Problem ============================================ #
prob = Problem()
prob.root = Constrained_MDO()

# ================================================ Add Driver ============================================== #
prob.driver = pyOptSparseDriver()
prob.driver.options['optimizer'] = 'ALPSO'
prob.driver.opt_settings = {'SwarmSize': 40, 'maxOuterIter': 30,\
				'maxInnerIter': 7, 'minInnerIter' : 7,  'seed': 2.0}

# prob.driver = ScipyOptimizer()
# prob.driver.options['optimizer'] = 'SLSQP'
# prob.root.fd_options['force_fd'] = True	
# prob.root.fd_options['form'] = 'forward'
# prob.root.fd_options['step_size'] = 1e-3,


# ===================================== Add design Varibles and Bounds ==================================== #
prob.driver.add_desvar('b_wing.b_wing',   	lower = 1,    upper = 3 )
prob.driver.add_desvar('C_r.C_r',        	lower = 0.3,  upper = 0.7)
prob.driver.add_desvar('t2.t2',           	lower = 0.6,  upper = 1.0)
prob.driver.add_desvar('t3.t3', 		  	lower = 0.6,  upper = 1.0)
prob.driver.add_desvar('t4.t4',			  	lower = 0.6,  upper = 1.0)
prob.driver.add_desvar('t5.t5',			  	lower = 0.6,  upper = 1.0)
prob.driver.add_desvar('b_htail.b_htail', 	lower = 0.6,  upper = 1.2)
prob.driver.add_desvar('C_r_t.C_r_t', 	  	lower = 0.15, upper = 0.3)
prob.driver.add_desvar('boom_len.boom_len', lower = 0.5,  upper = 1.5)
prob.driver.add_desvar('dist_LG.dist_LG', 	lower = 0.05, upper = 0.1)

prob.driver.add_desvar('camber.camber',               lower = np.array([0.10, 0.10, 0.10, 0.10, 0.10 ]),\
										              upper = np.array([0.15, 0.14, 0.14, 0.14, 0.14 ]))
prob.driver.add_desvar('max_camb_pos.max_camb_pos',   lower = np.array([0.35, 0.35, 0.35, 0.35, 0.35 ]),\
													  upper = np.array([0.50, 0.50, 0.50, 0.50, 0.50 ]))
prob.driver.add_desvar('thickness.thickness',         lower = np.array([0.10, 0.10, 0.10, 0.10, 0.10 ]),\
											          upper = np.array([0.15, 0.15, 0.15, 0.15, 0.15 ]) )
prob.driver.add_desvar('max_thick_pos.max_thick_pos', lower = np.array([0.25, 0.25, 0.25, 0.25, 0.25 ]),\
													  upper = np.array([0.45, 0.45, 0.45, 0.45, 0.45 ]) )

# add objective
prob.driver.add_objective('obj.score')



# =============== Setup & Run ================ #
prob.setup()

with writer.saving(fig, "OPT_#.mp4", 100):
	prob.run()


# ======================================== Post-Processing ============================================== #

print('================  Final Results ===================')
print('\n')
print('Score: ' + str(-1*prob['obj.score']))


post_process(prob)





# -- END OF FILE --
