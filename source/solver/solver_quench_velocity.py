
from source.solver.solver import Solver

class SolverQuenchVelocity(Solver):

    def __init__(self, ansys_commands, class_geometry, input_data, circuit):
        super.__init__(ansys_commands, class_geometry, input_data)
        self.circuit = circuit

        self.quench_label = 1
        self.quench_fronts = []
        self.quench_state_plots = []
        self.quench_temperature_plots = []

    def set_bcs(self):
        self.circuit.set_initial_current()
        self.circuit.set_ground()




