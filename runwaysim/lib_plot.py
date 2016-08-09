from scipy.optimize import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import os


def plot_geo_anim(Xle, Yle, C, Xle_t, Yle_t, C_t, writer, fig, a, b, c):
	wing_edge = Xle + [sum(x) for x in zip(Xle, C)][::-1] + [sum(x) for x in zip(Xle, C)] + [1*x for x in Xle[::-1]]
	wing_pos = Yle + Yle[::-1] + [-1*x for x in Yle] + [-1*x for x in Yle[::-1]]

	tail_edge = Xle_t + [sum(x) for x in zip(Xle_t, C_t)][::-1] + [sum(x) for x in zip(Xle_t, C_t)] + [1*x for x in Xle_t[::-1]]
	tail_pos = Yle_t + Yle_t[::-1] + [-1*x for x in Yle_t] + [-1*x for x in Yle_t[::-1]]

	self.a.set_data(wing_pos, wing_edge )
	self.b.set_data(tail_pos, tail_edge)
	# self.c.set_data([0, 0], [C[0], Xle_t[0]])
	self.c.set_data([0, Xle[0]/4.0], [C[0], Xle_t[0]])
	# plt.show()
	writer.grab_frame(figure = fig)

def plot_geo_final(Xle, Yle, C, Xle_t, Yle_t, C_t):
	wing_edge = Xle + [sum(x) for x in zip(Xle, C)][::-1] + [sum(x) for x in zip(Xle, C)] + [1*x for x in Xle[::-1]]
	wing_pos = Yle + Yle[::-1] + [-1*x for x in Yle] + [-1*x for x in Yle[::-1]]

	tail_edge = Xle_t + [sum(x) for x in zip(Xle_t, C_t)][::-1] + [sum(x) for x in zip(Xle_t, C_t)] + [1*x for x in Xle_t[::-1]]
	tail_pos = Yle_t + Yle_t[::-1] + [-1*x for x in Yle_t] + [-1*x for x in Yle_t[::-1]]

	plt.close('all')
	fig = plt.figure()

	ax1 = plt.subplot2grid((3, 3), (0, 0))
	ax2 = plt.subplot2grid((3, 3), (0, 1), colspan=2)
	ax3 = plt.subplot2grid((3, 3), (1, 0), colspan=2, rowspan=2)
	ax4 = plt.subplot2grid((3, 3), (1, 2), rowspan=2)

	ax1.plot(  wing_pos, wing_edge ,  'b-')
	ax2.plot(  wing_pos, wing_edge ,  'b-')
	ax3.plot( wing_pos, wing_edge, 'b-' )

	plt.tight_layout()
# 	plt.figure(1)
# 	plt.subplot(714)
# 	plt.ylabel('distance')
# 	plt.xlabel('time')
# 	plt.plot(time, dist, 'b')



	# plt.plot(  wing_pos, wing_edge ,  'b-')
	# plt.plot(  tail_pos, tail_edge ,  'r-')
	# plt.plot([0, 0], [C[0]/4.0, Xle_t[0]], 'g-')


