
from source.processor_pre.pre_processor import PreProcessor

class PreProcessorQuenchVelocity(PreProcessor):

    def __init__(self, mat_props, ansys_commands, input_data):
        PreProcessor.__init__(self, mat_props, ansys_commands, input_data)


