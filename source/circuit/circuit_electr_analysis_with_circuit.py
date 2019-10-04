
from source.circuit.circuit import Circuit

class CircuitElectricAnalysisWithCircuit(Circuit):

    def __init__(self, ansys_commands, class_geometry, input_data):
        Circuit.__init__(self, ansys_commands, class_geometry, input_data)

    def build_circuit(self):
        pass
