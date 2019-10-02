
from source.solver.solver import Solver

class SolverHeatBalance(Solver):

    def __init__(self, ansys_commands, class_geometry, input_data, circuit):
        super.__init__(ansys_commands, class_geometry, input_data)

    def set_bcs(self):
        pass
