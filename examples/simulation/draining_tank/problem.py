## ---------------------------------------------
# Example extracted from Example 32.2 in 
# Himmelblau, D. M., & Riggs, J. B. (2006). Basic principles and calculations in chemical engineering. FT press.
## ---------------------------------------------

# imports
import os
import numpy as np
import matplotlib.pyplot as plt

from cacao import Composite, SimulationProblem
from cacao.components import Tank, Orifice, Material, Content

def generate_model():
    model = Composite()
    model.time = np.linspace(0, 8e4, 50)

    # some constants
    water = Material(rho=1000)

    A = 16 # m2 area of tank
    A_orifice = 5e-4 # m2

    content_tank = Content(water, volume=10*A)
    c = 0.62

    #m0 = 10*A*RHO

    # tank model
    tank1 = Tank( model.time, A, content_tank)

    # orifice model
    orifice = Orifice(model.time, A_orifice, c)

    model.tank1 = tank1
    model.orifice = orifice
    model.connect(tank1, orifice)

    return model

model = generate_model()

sim = SimulationProblem(model)

result = sim.run()
model.change_inputs(result.x)


def case1_exact(t):
    A_orifice = 5e-4
    A = 16.0
    h0 = 10.0
    t0 = 0.0
    c = 0.62
    g = 9.81

    h = (np.sqrt(h0) - A_orifice*c*np.sqrt(2*g)*(t-t0)/(2*A))**2

    return h

h_exact = case1_exact(model.time)

# Mean squared errors
MSE = np.mean((model.tank1.height() - h_exact)**2)

plt.scatter(model.time, model.tank1.height(), s=80, facecolors='none', edgecolors='r', label='scipy');
plt.plot( model.time, case1_exact(model.time),'b', label='exact')
plt.xlabel('time (s)')
plt.ylabel('height (m)')
plt.legend()
plt.title(f'Draining tank. MSE = {MSE:.3e}')
plt.grid()

file_path = '/'.join(os.path.realpath(__file__).split('/')[:-1])
plt.savefig(os.path.join(file_path, 'result.png'))
plt.show()