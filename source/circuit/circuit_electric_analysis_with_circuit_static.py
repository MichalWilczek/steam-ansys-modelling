
from source.circuit.circuit_electr_analysis_with_circuit import CircuitElectricAnalysisWithCircuit

class CircuitElectricAnalysisWithCircuitStatic(CircuitElectricAnalysisWithCircuit):

    def __init__(self, ansys_commands, class_geometry, factory):
        CircuitElectricAnalysisWithCircuit.__init__(self, ansys_commands, class_geometry, factory)
        self.build_circuit()

    def set_circuit_bcs_in_analysis(self):
        pass
