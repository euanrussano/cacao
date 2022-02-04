##-- Workaround to make the cacao library in path if it's not installed but in parent directory
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..')))
##--

from cacao.components.generics import Variable, Block, Constraint
from cacao import Composite, SimulationProblem

model = Composite()

eqs = Block()
eqs.x = Variable()
eqs.y = Variable()

eqs.eq1 = Constraint(lambda block: block.x()+2*block.y()-0)
eqs.eq2 = Constraint(lambda block: block.x()**2+block.y()**2-1)

model.eqs = eqs
sim = SimulationProblem(model)

result = sim.run()
model.change_inputs(result.x)

print('x = ', model.eqs.x())
print('y = ', model.eqs.y())
