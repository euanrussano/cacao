# Cacao framework
A library for dynamic simulation/ optimization.

### Installation
```
pip install cacao
```

### Get started
Create a gravity drained tank. The mass balance is:

<img src="https://render.githubusercontent.com/render/math?math=\frac{dV}{dt}=Q_{in}-Q_{out}">

The height of fluid  in the reservoir is:

<img src="https://render.githubusercontent.com/render/math?math=h=\frac{V}{A}">

Considering a constant inflow, the flow at the outlet can be considered, according Bernoulli equation:

<img src="https://render.githubusercontent.com/render/math?math=Q_{out}=Cv\sqrt{h}">

```python
import numpy as np
import csv # for output

from cacao.hydraulics import FlowSource, FlowRelease, Reservoir
from cacao.flowsheet import Flowsheet
# ============================
# Model
# ============================
A = 0.2 # m  - Cross section area of reservoir
Cv = 0.5 # -- outlet coefficient

q_in = lambda t: 0.5 # m3/s constant inflow

inflow = FlowSource(q_in, flowrate="Qin")
release1 = FlowRelease(Cv, flowrate="Q1")

reservoir1 = Reservoir(A, 0.0, volume="V1", height="h1")

flowsheet = Flowsheet([inflow, reservoir1, release1])
flowsheet.connect(inflow, reservoir1)
flowsheet.connect(reservoir1, release1)

# ============================
# Run simulation
# ============================

n_nodes = 6 # collocation points
dt = 0.1 # s -- time range to perform collocation
time = 0.0 # s -- simulation start time
tf = 10.0 # s -- simulation final time
flowsheet.initialize(n_nodes=n_nodes, dt=dt, time=time)
timesteps, states, outputs = flowsheet.update_until(tf=tf)

# ============================
# Generate output
# ============================

# merge dictionaries
results = {**states, **outputs}
results['time'] = timesteps

# write to file
with open('results.csv', 'w') as outfile:
    writer = csv.writer(outfile, delimiter = ",")
    writer.writerow(results.keys())
    writer.writerows(zip(*results.values()))
```
