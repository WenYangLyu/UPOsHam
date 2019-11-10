# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 16:45:58 2019

@author: Wenyang Lyu and Shibabrat Naik
"""

import numpy as np
import matplotlib.pyplot as plt
#from scipy.integrate import odeint,quad,trapz,solve_ivp
from scipy.integrate import solve_ivp
#import math
#from IPython.display import Image # for Notebook
#from IPython.core.display import HTML
from mpl_toolkits.mplot3d import Axes3D
#from numpy import linalg as LA
#import scipy.linalg as linalg
#from scipy.optimize import fsolve
#import time
#from functools import partial
import sys
sys.path.append('./src/')
import tpcd_UPOsHam2dof ### import module xxx where xxx is the name of the python file xxx.py 
import diffcorr_UPOsHam2dof


#from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
from matplotlib import cm
#from pylab import rcParams
mpl.rcParams['mathtext.fontset'] = 'cm'
mpl.rcParams['mathtext.rm'] = 'serif'

#from scipy import optimize


#% Begin problem specific functions
def init_guess_eqpt_coupled(eqNum, par):
    """
    Returns configuration space coordinates of the equilibrium points according to the index:
    Saddle (EQNUM=1)
    Centre (EQNUM=2,3)
    """
    
    if eqNum == 1:
        x0 = [0, 0]
    elif eqNum == 2:
        x0 = [np.sqrt(par[3]-par[6]/par[4]),0] 
    elif eqNum == 3:
        x0 = [-np.sqrt(par[3]-par[6]/par[4]),0] 
    
    return x0

def grad_pot_coupled(x, par):
    """Returns the gradient of the potential energy function V(x,y)
    """ 
    
    dVdx = (-par[3]+par[6])*x[0]+par[4]*(x[0])**3-par[6]*x[1]
    dVdy = (par[5]+par[6])*x[1]-par[6]*x[0]
    
    F = [-dVdx, -dVdy]
    
    return F

def pot_energy_coupled(x, y, par):
    """Returns the potential energy function V(x,y)
    """
    
    return -0.5*par[3]*x**2+0.25*par[4]*x**4 +0.5*par[5]*y**2+0.5*par[6]*(x-y)**2


def varEqns_coupled(t,PHI,par):
    """    
    Returns the state transition matrix , PHI(t,t0), where Df(t) is the Jacobian of the 
    Hamiltonian vector field
    
    d PHI(t, t0)
    ------------ =  Df(t) * PHI(t, t0)
        dt
    
    """
    
    phi = PHI[0:16]
    phimatrix  = np.reshape(PHI[0:16],(4,4))
    x,y,px,py = PHI[16:20]
    
    
    # The first order derivative of the potential energy.
    dVdx = (-par[3]+par[6])*x+par[4]*x**3-par[6]*y
    dVdy = (par[5]+par[6])*y-par[6]*x

    # The second order derivative of the potential energy. 
    d2Vdx2 = -par[3]+par[6]+par[4]*3*x**2
        
    d2Vdy2 = par[5]+par[6]

    d2Vdydx = -par[6]

    
    d2Vdxdy = d2Vdydx    

    Df    = np.array([[  0,     0,    par[0],    0],
              [0,     0,    0,    par[1]],
              [-d2Vdx2,  -d2Vdydx,   0,    0],
              [-d2Vdxdy, -d2Vdy2,    0,    0]])

    
    phidot = np.matmul(Df, phimatrix) # variational equation

    PHIdot        = np.zeros(20)
    PHIdot[0:16]  = np.reshape(phidot,(1,16)) 
    PHIdot[16]    = px/par[0]
    PHIdot[17]    = py/par[1]
    PHIdot[18]    = -dVdx 
    PHIdot[19]    = -dVdy
    
    return list(PHIdot)


def ham2dof_coupled(t, x, par):
    """ 
    Returns the Hamiltonian vector field (Hamilton's equations of motion) 
    """
    
    xDot = np.zeros(4)
    
    dVdx = (-par[3]+par[6])*x[0]+par[4]*(x[0])**3-par[6]*x[1]
    dVdy = (par[5]+par[6])*x[1]-par[6]*x[0]
        
    xDot[0] = x[2]/par[0]
    xDot[1] = x[3]/par[1]
    xDot[2] = -dVdx 
    xDot[3] = -dVdy
    
    return list(xDot)    

def half_period_coupled(t, x, par):
    """
    Returns the turning point where we want to stop the integration                           
    
    pxDot = x[0]
    pyDot = x[1]
    xDot = x[2]
    yDot = x[3]
    """
    
    terminal = True
    # The zero can be approached from either direction
    direction = 0 #0: all directions of crossing
    
    return x[3]


#% End problem specific functions


#%% Setting up parameters and global variables
N = 4          # dimension of phase space
omega=1.00
EPSILON_S = 0.0 #Energy of the saddle
alpha = 1.00
beta = 1.00
epsilon= 1e-1
parameters = np.array([1,omega, EPSILON_S, alpha, beta,omega,epsilon])
eqNum = 1 
#model = 'coupled'
#eqPt = diffcorr_UPOsHam2dof.get_eq_pts(eqNum,model, parameters)
eqPt = diffcorr_UPOsHam2dof.get_eq_pts(eqNum, init_guess_eqpt_coupled, \
                                       grad_pot_coupled, parameters)

#energy of the saddle eq pt
eSaddle = diffcorr_UPOsHam2dof.get_total_energy([eqPt[0],eqPt[1],0,0], pot_energy_coupled, \
                                                parameters)

#%% Load Data


deltaE = 0.10
eSaddle = 0.0 # energy of the saddle
#po_fam_file = open("./data/1111x0_newmethod_deltaE%s_coupled.txt" %(deltaE),'a+')
#po_fam_file = open("1111x0_tpcd_deltaE%s_coupled.txt" %(deltaE),'a+')
data_path = "./data/"
po_fam_file = "x0_tpcd_deltaE%s_coupled.txt" %(deltaE)
print('Loading the periodic orbit family from data file',po_fam_file,'\n') 
#x0podata = np.loadtxt(po_fam_file.name)
x0podata = np.loadtxt(data_path + po_fam_file)

#po_fam_file.close()
x0po_1_tpcd = x0podata


#po_fam_file = open("./data/1111x0_turningpoint_deltaE%s_coupled.txt" %(deltaE),'a+')
po_fam_file = "x0_turningpoint_deltaE%s_coupled.txt" %(deltaE)
print('Loading the periodic orbit family from data file',po_fam_file,'\n') 
#x0podata = np.loadtxt(po_fam_file.name)
x0podata = np.loadtxt(data_path + po_fam_file)

#po_fam_file.close()
x0po_1_turningpoint = x0podata


#po_fam_file = open("./data/1111x0_diffcorr_deltaE%s_coupled.txt" %(deltaE),'a+')
po_fam_file = "x0_diffcorr_deltaE%s_coupled.txt" %(deltaE)
print('Loading the periodic orbit family from data file',po_fam_file,'\n') 
#x0podata = np.loadtxt(po_fam_file.name)
x0podata = np.loadtxt(data_path + po_fam_file)
#po_fam_file.close()
x0po_1_diffcorr = x0podata[0:4]

#%%
TSPAN = [0,30]
plt.close('all')
axis_fs = 15
RelTol = 3.e-10
AbsTol = 1.e-10

#f = lambda t,x : tpcd_UPOsHam2dof.Ham2dof(model,t,x,parameters)
#soln = solve_ivp(f, TSPAN, x0po_1_tpcd[-1,0:4],method='RK45',dense_output=True, events = lambda t,x : tpcd_UPOsHam2dof.half_period(t,x,model),rtol=RelTol, atol=AbsTol)
f= lambda t,x: ham2dof_coupled(t,x,parameters)
soln = solve_ivp(f, TSPAN, x0po_1_tpcd[-1,0:4],method='RK45',dense_output=True, \
                 events = lambda t,x : half_period_coupled(t,x,parameters), \
                 rtol=RelTol, atol=AbsTol)
te = soln.t_events[0]
tt = [0,te[2]]
#t,x,phi_t1,PHI = diffcorr_UPOsHam2dof.stateTransitMat(tt,x0po_1_tpcd[-1,0:4],parameters,model)
t,x,phi_t1,PHI = diffcorr_UPOsHam2dof.stateTransitMat(tt, x0po_1_tpcd[-1,0:4], parameters, \
                                                      varEqns_coupled)

ax = plt.gca(projection='3d')
ax.plot(x[:,0],x[:,1],x[:,3],'-',label='$\Delta E$ = 0.1, using tpcd')
ax.scatter(x[0,0],x[0,1],x[0,3],s=20,marker='*')
ax.plot(x[:,0], x[:,1], zs=0, zdir='z')

#f = lambda t,x : tpcd_UPOsHam2dof.Ham2dof(model,t,x,parameters)
#soln = solve_ivp(f, TSPAN, x0po_1_diffcorr,method='RK45',dense_output=True, events = lambda t,x : tpcd_UPOsHam2dof.half_period(t,x,model),rtol=RelTol, atol=AbsTol)
f = lambda t,x: ham2dof_coupled(t,x,parameters)
soln = solve_ivp(f, TSPAN, x0po_1_diffcorr,method='RK45',dense_output=True, \
                 events = lambda t,x : half_period_coupled(t,x,parameters), \
                 rtol=RelTol, atol=AbsTol)

te = soln.t_events[0]
tt = [0,te[2]]
#t,x,phi_t1,PHI = diffcorr_UPOsHam2dof.stateTransitMat(tt,x0po_1_diffcorr,parameters,model)
t,x,phi_t1,PHI = diffcorr_UPOsHam2dof.stateTransitMat(tt, x0po_1_tpcd[-1,0:4], parameters, \
                                                      varEqns_coupled)

#ax = plt.gca(projection='3d')
ax.plot(x[:,0],x[:,1],x[:,3],':',label='$\Delta E$ = 0.1, using dcnc')
ax.scatter(x[0,0],x[0,1],x[0,3],s=20,marker='*')
ax.plot(x[:,0], x[:,1], zs=0, zdir='z')

#f = lambda t,x : tpcd_UPOsHam2dof.Ham2dof(model,t,x,parameters)
#soln = solve_ivp(f, TSPAN, x0po_1_turningpoint[-1,0:4],method='RK45',dense_output=True, events = lambda t,x : tpcd_UPOsHam2dof.half_period(t,x,model),rtol=RelTol, atol=AbsTol)
f = lambda t,x: ham2dof_coupled(t,x,parameters)
soln = solve_ivp(f, TSPAN, x0po_1_turningpoint[-1,0:4], method='RK45',dense_output=True, \
                 events = lambda t,x : half_period_coupled(t,x,parameters), \
                 rtol=RelTol, atol=AbsTol)

te = soln.t_events[0]
tt = [0,te[2]]
#t,x,phi_t1,PHI = diffcorr_UPOsHam2dof.stateTransitMat(tt,x0po_1_turningpoint[-1,0:4],parameters,model)
t,x,phi_t1,PHI = diffcorr_UPOsHam2dof.stateTransitMat(tt, x0po_1_turningpoint[-1,0:4], parameters, \
                                                      varEqns_coupled)

#ax = plt.gca(projection='3d')
ax.plot(x[:,0],x[:,1],x[:,3],'-.',label='$\Delta E$ = 0.1, using tp')
ax.scatter(x[0,0],x[0,1],x[0,3],s=20,marker='*')
ax.plot(x[:,0], x[:,1], zs=0, zdir='z')



ax = plt.gca(projection='3d')
resX = 100
xVec = np.linspace(-4,4,resX)
yVec = np.linspace(-4,4,resX)
xMat, yMat = np.meshgrid(xVec, yVec)
#cset1 = ax.contour(xMat, yMat, uncoupled_tpcd.get_pot_surf_proj(xVec, yVec,parameters), [0.001,0.1,1,2,4],
#                       linewidths = 1.0, cmap=cm.viridis, alpha = 0.8)
cset2 = ax.contour(xMat, yMat, \
                   diffcorr_UPOsHam2dof.get_pot_surf_proj(xVec, yVec, pot_energy_coupled, \
                                                          parameters), 0.1,zdir='z', offset=0, \
                   linewidths = 1.0, cmap=cm.viridis, alpha = 0.8)
ax.scatter(eqPt[0], eqPt[1], s = 100, c = 'r', marker = 'X')
ax.set_xlabel('$x$', fontsize=axis_fs)
ax.set_ylabel('$y$', fontsize=axis_fs)
ax.set_zlabel('$p_y$', fontsize=axis_fs)
legend = ax.legend(loc='upper left')

ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_zlim(-0.5, 0.5)
plt.grid()
plt.show()
plt.savefig('comparison_coupled.pdf',format='pdf',bbox_inches='tight')


