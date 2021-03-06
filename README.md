# Cacao framework
A library for dynamic simulation/ optimization.

### Installation
```
pip install cacao
```

### Get started

Simulation of gravity drained tank, initially filed with water 10 meters high. The tank has constant cross-section (16 m^2) and an orifice at the bottom with 5 cm^2 area. Example extracted from:

Himmelblau, D. M., & Riggs, J. B. (2006). Basic principles and calculations in chemical engineering. FT press.

```python
# imports
import numpy as np
import matplotlib.pyplot as plt

from cacao import Composite, SimulationProblem
from cacao.components import Tank, Orifice, Material, Content

model = Composite()
model.time = np.linspace(0, 8e4, 50)

# tank
water = Material(rho=1000)
area = 16 # m^2
initial_volume = 10*area
content_tank = Content(water, volume=initial_volume)  
tank = Tank( model.time, area, content_tank)

# orifice
A_orifice = 5e-4 # m2
c = 0.62 # orifice flow coefficient
orifice = Orifice(model.time, A_orifice, c)

model.tank = tank
model.orifice = orifice
model.connect(tank, orifice)

sim = SimulationProblem(model)

result = sim.run()
model.change_inputs(result.x)


plt.plot(model.time, model.tank1.height())
plt.show()
```
