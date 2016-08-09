
import subprocess as sp
import os
import shutil
import sys
import string
from time import localtime, strftime
# 
# avlpath = '/home/josh/Documents/avl/bin/avl'
#avlpath = r'D:\home\josh\Documents\avl\bin\avl.exe'

v_cruise = 13.00
Rho = 1.225

avlpath = '/home/josh/Documents/Research/MACHMDO/runwaysim/AVL/avl'


def avl_run(filename, alpha_start, alpha_end ):

    def Cmd(cmd):
        ps.stdin.write(cmd+'\n')


    try:
        os.remove(filename+'_data.dat')
    except :
        pass

    try:
        os.remove('stab.txt')
    except:
        pass

    #    print ("no such file")
    # run avl
    ps = sp.Popen(avlpath,stdin=sp.PIPE,stderr=sp.PIPE,stdout=sp.PIPE)
    ps.stderr.close()

    Cmd('PLOP')
    Cmd('G')
    Cmd(' ')

    Cmd('load '+filename+'.txt')

    
    # Apply mass file 
    Cmd('Mass' + filename +'.mass')
    Cmd('MSET 0')

    Cmd('OPER')
    # Cmd('g')
    # Cmd(' ')

    # Cmd('M')
    # Cmd('V ' + str(v_cruise))
    # Cmd('d ' + str(Rho))

    # Cmd('d1 rm 0')
    # Cmd('d3 ym 0')

    Cmd('a a ' + str(alpha_start))
    Cmd('x')
    # Cmd('t')
    # Cmd(' ')
    Cmd('ST')
    Cmd('stab.txt')
    Cmd('w')
    Cmd(filename+'_data.dat')  # output file

    for i in range(alpha_start + 1, alpha_end + 1):
        Cmd('a a ' + str(i))
        Cmd('x')
        Cmd('w')  
        Cmd(' ')



    Cmd(' ')
    Cmd(' ')          
          
    Cmd('quit')  # exit

    ps.stdout.close()
    ps.stdin.close()
    ps.wait()


def getData_AVL(filename):
    
    f = open(filename, 'r')
    flines = f.readlines()

    alpha = []
    CL = []
    CD = []
    CM = []
    elev_def = []


    for i in range(0,len(flines)):
         
        words = string.split(flines[i]) 
        if len(words) > 1:
            if 'Alpha' in words:
                alpha.append(float(words[2]))
            elif 'CLtot' in words:
                CL.append(float(words[2]))
            elif 'CDtot' in words:
                CD.append(float(words[2]))
            elif 'Cmtot' in words:
                CM.append(float(words[5]))
            elif 'Elevator' in words:
                elev_def.append(float(words[2]))

    LtoD = [a/b for a,b in zip(CL,CD)]

    return (alpha, CL, CD, CM, LtoD, elev_def)

def getNP_AVL(filename):

    f = open(filename, 'r')
    flines = f.readlines()

    # print(len(flines))

    words = string.split(flines[64])

    x_np = float(words[4])


    return x_np
