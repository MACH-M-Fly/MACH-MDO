import sys
sys.path.insert(0, '/home/josh/Documents/Research/MACHMDO')

from runwaysim.lib_runwaysim_small import *
# from constants import *
from forces import *

print(filename)

#find time to takeoff
# takeoff,dist, vel, ang, ang_vel, time =  runway_sim_small(CL, CD, CM, CL_tail_noflap, CL_tail_flap)
takeoff,dist, vel, ang, ang_vel, time =  runway_sim_small(CL, CD, CM, CL_tail_noflap, CL_tail_flap, Sref_wing, weight, boom_len, dist_LG, Cref, I_G)

print(takeoff)
print(dist)
print(vel)
print(ang)
print(ang_vel)
print(time)
# if takeoff == 0 