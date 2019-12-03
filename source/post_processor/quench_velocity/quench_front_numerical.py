
from source.post_processor.quench_velocity.quench_front import QuenchFront
from source.post_processor.quench_velocity.quench_velocity_map import QuenchVelocityMap

class QuenchFrontNum(QuenchFront, QuenchVelocityMap):

    def __init__(self, x_down, x_up, label, class_geometry, factory, testunit=False):
        self.factory = factory
        self.testunit = testunit
        self.class_geometry = class_geometry
        QuenchFront.__init__(self, x_down, x_up, label, class_geometry, testunit=self.testunit)
        QuenchVelocityMap.__init__(self, factory)
        self.quench_velocity_up = None
        self.quench_velocity_down = None

    def merge(self, qf, testunit=False):
        """
        :param qf: QuenchFront object
        :return: New quench QuenchFront object merged from quench front and qf
        """
        x_down_new = min(self.x_down, qf.x_down)
        x_up_new = max(self.x_up, qf.x_up)
        return QuenchFrontNum(x_down_new, x_up_new, str(self.label) + "_" + str(qf.label),
                              self.class_geometry, testunit=testunit, factory=self.factory)

    def q_v_to_string(self):
        return "QUENCH FRONT NO {}; quench_velocity [m/s]: up = {}, down = {}\n".format(
            self.label, self.quench_velocity_up, self.quench_velocity_down)

    @staticmethod
    def return_magnetic_field_of_winding(mag_field_map, front_winding_numbers):
        mag_field_list = []
        for winding_down in front_winding_numbers:
            mag_field_list.append(mag_field_map[winding_down])
        return max(mag_field_list)

    def return_quench_front_position(self, initial_time, final_time, min_length, max_length, mag_field_map, current):
        """
        Calculates quench front position in meters and nodal numbers
        :param initial_time: initial time of integration as float
        :param final_time: final time of integration as float
        :param min_length: minimum coil length as float
        :param max_length: maximum coil length as float
        :param mag_field_map:
        :param current:
        """
        mag_field_front_up = self.return_magnetic_field_of_winding(mag_field_map, self.front_up_winding_numbers)
        mag_field_front_down = self.return_magnetic_field_of_winding(mag_field_map, self.front_down_winding_numbers)

        self.quench_velocity_up = self.get_quench_velocity(mag_field_front_up, current)
        self.quench_velocity_down = self.get_quench_velocity(mag_field_front_down, current)

        q_length_up = self.calculate_q_length(initial_time, final_time, quench_velocity=self.quench_velocity_up)
        q_length_down = self.calculate_q_length(initial_time, final_time, quench_velocity=self.quench_velocity_down)

        self.calculate_quench_front_position(q_length_down=q_length_down, q_length_up=q_length_up,
                                             min_length=min_length, max_length=max_length)
        print(self.q_v_to_string())
        self.convert_quench_front_to_nodes(self.coil_geometry)
        self.find_front_winding_numbers(self.coil_data)
