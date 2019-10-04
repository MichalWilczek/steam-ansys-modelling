
from source.circuit.circuit_electr_analysis_with_circuit import CircuitElectricAnalysisWithCircuit

class CircuitElectricAnalysisWithCircuitTransient(CircuitElectricAnalysisWithCircuit):

    def __init__(self, ansys_commands, class_geometry, input_data):
        CircuitElectricAnalysisWithCircuit.__init__(self, ansys_commands, class_geometry, input_data)
        self.build_circuit()

    def set_circuit_bcs_in_analysis(self):
        pass
