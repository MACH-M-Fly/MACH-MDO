from lib_plot import *

result_score = -1*-64.9773732627
result_Sref = 0.542432374002
b_wing = 1.11973267514
C_r = 0.639696031882
t2 = 0.848381543484
t3 = 0.896410543238
t4 = 0.93080487922
t5 = 0.600028235866
b_htail = 0.6
C_r_t = 0.151096582615
dist_LG = 0.0967751786853
boom_len = 0.500050752398

C = [C_r, C_r*t2, C_r*t2*t3, C_r*t2*t3*t4,  C_r*t2*t3*t4*t5]

b_wing = b_wing

boom_len = boom_len
dist_LG = dist_LG

Yle =  [0, 1*b_wing/8,  b_wing/4, 3*b_wing/8, b_wing/2]
Sref = b_wing/8*(C[0] + 2*C[1] + 2*C[2] + 2*C[3] + C[4])

Xle =  [0]

for i in range(0, len(C)-1):
	Xle.append((C[i] - C[i +1])/4 + Xle[i])


Xle_t =[boom_len + C[0]/4.0, boom_len + C[0]/4.0]
Yle_t = [0, b_htail/2.0]
C_t = [C_r_t , C_r_t]


x_cg = 0.109180942284
NP =  0.196274

plot_geo_final(Xle, Yle, C, Xle_t, Yle_t, C_t, x_cg, NP, result_score)

plt.savefig('OPT_#.pdf', bbox_inches='tight')
