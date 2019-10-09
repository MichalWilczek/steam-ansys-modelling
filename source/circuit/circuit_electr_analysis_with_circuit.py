
from source.circuit.circuit import Circuit

class CircuitElectricAnalysisWithCircuit(Circuit):

    def __init__(self, ansys_commands, class_geometry, factory):
        Circuit.__init__(self, ansys_commands, class_geometry, factory)

    def build_circuit(self):
        pass
