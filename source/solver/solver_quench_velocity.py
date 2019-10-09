
from source.solver.solver import Solver


class SolverQuenchVelocity(Solver):

    def __init__(self, factory, ansys_commands, class_geometry,
                 circuit, ic_temperature_class, mat_props, mag_map):
        Solver.__init__(self, factory, ansys_commands, class_geometry,
                        circuit, ic_temperature_class, mat_props, mag_map)
        self.circuit = circuit


