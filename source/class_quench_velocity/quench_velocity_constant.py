
from source.class_quench_velocity.quench_velocity import QuenchFront


class QuenchFrontConst(QuenchFront):

    def __init__(self, x_down, x_up, label, coil_geometry, coil_data, testunit=False):
        self.testunit = testunit
        QuenchFront.__init__(self, x_down, x_up, label, coil_geometry, coil_data, testunit=self.testunit)
        self.q_v = 7.5       # [m/s]

    def merge(self, qf, testunit=False):
        """
        :param qf: QuenchFront object
        :return: New quench QuenchFront object merged from quench front and qf
        """
        x_down_new = min(self.x_down, qf.x_down)
        x_up_new = max(self.x_up, qf.x_up)
        return QuenchFrontConst(x_down_new, x_up_new, str(self.label) + "_" + str(qf.label),
                                self.coil_geometry, self.coil_data, testunit)

    def return_quench_front_position(self, initial_time, final_time, min_length, max_length, **kwargs):
        """
        Calculates quench front position in meters and nodal numbers
        :param initial_time: initial time of integration as float
        :param final_time: final time of integration as float
        :param min_length: minimum coil length as float
        :param max_length: maximum coil length as float
        """
        q_length = self.calculate_q_length(initial_time, final_time)
        self.calculate_quench_front_position(q_length, q_length, min_length, max_length)
        self.convert_quench_front_to_nodes(self.coil_geometry)

    def calculate_q_length(self, initial_time, final_time):
        """
        Calculates quench front position after a given time
        :param initial_time: initial time of integration as float
        :param final_time: final time of integration as float
        :return: quench integration length as float
        """
        return (final_time-initial_time)*self.q_v



