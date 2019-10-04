
from source.solver.solver import Solver


class SolverQuenchVelocity(Solver):

    def __init__(self, ansys_commands, class_geometry, input_data, circuit, ic_temperature_class, mat_props, mag_map):
        Solver.__init__(self, ansys_commands, class_geometry, input_data,
                        circuit, ic_temperature_class, mat_props, mag_map)
        self.circuit = circuit


