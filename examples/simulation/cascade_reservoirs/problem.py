## ---------------------------------------------
# Example extracted from
# http://apmonitor.com/do/index.php/Main/ModelFormulation
# Exercise
# Objective: Formulate a dynamic model with model quantities such as 
# constants, parameters, and variables and model expressions such as intermediates and equations. 
# Use time-varying inputs, initial conditions, and mass balance equations to specify the problem inputs and dynamics.
# Create a MATLAB or Python script to simulate and display the results. Estimated Time: 2 hours
## ---------------------------------------------
##-- Workaround to make the cacao library in path if it's not installed but in parent directory
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..')))
##--

# imports
import numpy as np
import matplotlib.pyplot as plt

from cacao import Composite, SimulationProblem
from cacao.components import Tank, Orifice, Stream, Material, Content

# some constants
water = Material(rho=1000)

RHO = 1000 # kg/m3 density of water
g = 9.81 # m/s2 gravity acceleration

# Outflow coefficients
C1 = 0.03/np.sqrt(2*g)*1e9
C2 = 0.015/np.sqrt(2*g)*1e9
C3 = 0.060/np.sqrt(2*g)*1e9
C4 = 0.0/np.sqrt(2*g)*1e9

# Area of Reservoir / Lake (m2)
A1 = 13.4*1e6
A2 = 12.0*1e6
A3 = 384.5*1e6
A4 = 4400*1e6

# Initial Mass water in Reservoir / Lake (kg)
M1 = Content(water, volume=0.26*1e9)
M2 = Content(water, volume=0.18*1e9)
M3 = Content(water, volume=0.68*1e9)
M4 = Content(water, volume=22.0*1e9)

model = Composite()
model.time = np.linspace(0.0, 1.0, 13*2)

# Boundary inflow and constant outflows
# Evaporation Rates (kg/yr)
model.Vevap1 = Stream(model.time, 1e-5*1e3 * A1 * RHO)
model.Vevap2 = Stream(model.time, 1e-5*1e3 * A2 * RHO)
model.Vevap3 = Stream(model.time, 1e-5*1e3 * A3 * RHO)
model.Vevap4 = Stream(model.time, 0.5e-5*1e3 * A4 * RHO) # for salt water (Great Salt Lake)

# Inflow Rates (kg/yr)
tin = np.linspace(0, 1, 13)
vin = [0.13,0.13, 0.13, 0.21,0.21,0.21,0.13, 0.13,0.13,0.13,0.13,0.13,0.13] # km3/year
mass_in = list(map(lambda x: x*RHO*1e9, vin))
model.Vflow_in1 = Stream(model.time, tin, mass_in )

# Usage Requirements (kg/yr)
model.Vuse1 = Stream(model.time, 0.03*RHO*1e9)
model.Vuse2 = Stream(model.time, 0.05*RHO*1e9)
model.Vuse3 = Stream(model.time, 0.02*RHO*1e9)
model.Vuse4 = Stream(model.time, 0.00*RHO*1e9)

# reservoirs
model.jordanelle = Tank( model.time, A1, M1)
model.creek = Tank( model.time, A2, M2)
model.utah = Tank( model.time, A3, M3)
model.lake = Tank( model.time, A4, M4)

# orifices
model.orifice1 = Orifice(model.time, 1, C1)
model.orifice2 = Orifice(model.time, 1, C2)
model.orifice3 = Orifice(model.time, 1, C3)
model.orifice4 = Orifice(model.time, 1, C4)

# connections inflow
model.connect(model.Vflow_in1, model.jordanelle)

# connections orifices
model.connect(model.jordanelle, model.orifice1)
model.connect(model.orifice1, model.creek)
model.connect(model.creek, model.orifice2)
model.connect(model.orifice2, model.utah)
model.connect(model.utah, model.orifice3)
model.connect(model.orifice3, model.lake)
model.connect(model.lake, model.orifice4)

# connections evaporation
model.connect(model.jordanelle, model.Vevap1)
model.connect(model.creek, model.Vevap2)
model.connect(model.utah, model.Vevap3)
model.connect(model.lake, model.Vevap4)

# connections usage
model.connect(model.jordanelle, model.Vuse1)
model.connect(model.creek, model.Vuse2)
model.connect(model.utah, model.Vuse3)
model.connect(model.lake, model.Vuse4)

sim = SimulationProblem(model)

result = sim.run()
model.change_inputs(result.x)

# Results from APMonitor
time_exact = [0, 1.00000002980232, 2.00000005960464, 3, 4.00000011920929, 4.99999988079071, 6, 6.99999976158142, 8.00000023841858, 9, 9.99999976158142, 11.0000002384186, 12]
jordanelle_exact = [19.4029846191406,
19.2043533325195,
19.0098934173584,
18.8221912384033,
19.1280479431152,
19.4274520874023,
19.7180080413818,
19.5127811431885,
19.3118343353271,
19.1151084899902,
18.9225368499756,
18.7340507507324,
18.54958152771,
]


plt.scatter(model.time*12, model.jordanelle.height(), s=80, facecolors='none', edgecolors='r', label='jordan')
plt.scatter(model.time*12, model.creek.height(), s=80, facecolors='none', edgecolors='r', label='creek')
plt.plot(time_exact, jordanelle_exact,'-r', label='APMonitor')
plt.xlabel('time (s)')
plt.ylabel('height (m)')
plt.legend()
plt.title(f'Cascade of reservoirs')
plt.grid()
plt.show()

