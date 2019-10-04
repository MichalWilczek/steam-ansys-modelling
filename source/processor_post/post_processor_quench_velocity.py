
from source.processor_post.post_processor import PostProcessor

class PostProcessorQuenchVelocity(PostProcessor):

    def __init__(self, class_geometry, ansys_commands, v_quench, solver, input_data):
        PostProcessor.__init__(self, class_geometry, ansys_commands, v_quench, solver, input_data)
