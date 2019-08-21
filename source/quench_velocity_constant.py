
from source.quench_velocity import QuenchFront


class QuenchFrontConst(QuenchFront):

    def __init__(self, x_down, x_up, label, **kwargs):
        QuenchFront.__init__(self, x_down, x_up, label)
        self.q_v = 1.0       # [m/s]

    def return_quench_front_position(self, initial_time, final_time, min_length, max_length):
        q_length = self.calculate_q_length(initial_time, final_time)
        self.calculate_quench_front_position(q_length, min_length, max_length)

    def calculate_q_length(self, initial_time, final_time):
        return (final_time-initial_time)*self.q_v



