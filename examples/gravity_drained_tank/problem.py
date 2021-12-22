# ============================
# Imports
# ============================
##-- Workaround to make the cacao library in path if it's not installed but in parent directory
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
##--

import numpy as np
from scipy import interpolate
import csv

from cacao.hydraulics import FlowSource, FlowRelease, Reservoir
from cacao.flowsheet import Flowsheet
# ============================
# Model
# ============================
A = 0.2
Cv = 0.5

t_qin = np.arange(0, 11, 0.1)
q_qin = np.where(t_qin < 5.0, 0.4,0.3)
q_in = interpolate.interp1d(t_qin, q_qin, kind='previous')

inflow = FlowSource(q_in, flowrate="Qin")
release1 = FlowRelease(Cv, flowrate="Q1")
release2 = FlowRelease(Cv, flowrate="Q2")

reservoir1 = Reservoir(A, 0.0, volume="V1", height="h1")
reservoir2 = Reservoir(A, 0.0, volume="V2", height="h2")

flowsheet = Flowsheet([inflow, reservoir1, release1, reservoir2, release2])
flowsheet.connect(inflow, reservoir1)
flowsheet.connect(reservoir1, release1)
flowsheet.connect(release1, reservoir2)
flowsheet.connect(reservoir2, release2)

# ============================
# Run simulation
# ============================

flowsheet.initialize(n_nodes=6, dt=0.1, time=0.0)
timesteps, states, outputs = flowsheet.update_until(tf=10.0)

# ============================
# Generate output
# ============================

# merge dictionaries
results = {**states, **outputs}
results['time'] = timesteps

# order of output
with open('results.csv', 'w') as outfile:
    writer = csv.writer(outfile, delimiter = ",")
    writer.writerow(results.keys())
    writer.writerows(zip(*results.values()))