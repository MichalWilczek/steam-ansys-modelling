
from source.post_processor.quench_velocity.quench_front import QuenchFront
from source.post_processor.quench_velocity.quench_velocity_map import QuenchVelocityMap
import numpy as np
import scipy.integrate


class QuenchFrontNum(QuenchFront, QuenchVelocityMap):

    def __init__(self, x_down, x_up, label, class_geometry, factory, testunit=False):
        self.factory = factory
        self.testunit = testunit
        self.class_geometry = class_geometry
        QuenchFront.__init__(self, x_down, x_up, label, class_geometry, testunit=self.testunit)
        if not testunit:
            QuenchVelocityMap.__init__(self, factory)
            self.quench_velocity_up = None
            self.quench_velocity_down = None
            self.q_length_up = None
            self.q_length_down = None

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
        return "QUENCH FRONT NO {}; instantaneous quench_velocity [m/s]: up = {}, down = {}\n".format(
            self.label, self.quench_velocity_up, self.quench_velocity_down)

    def q_integrated_length_to_string(self):
        return "\nQUENCH FRONT NO {}; integrated quench length [m]: up = {}, down = {}".format(
            self.label, self.q_length_up, self.q_length_down)

    def return_quench_front_position(self, initial_time, final_time, min_length,
                                     max_length, mag_field_map, f_division=200):
        """
        Calculates quench front position in meters and nodal numbers
        :param initial_time: initial time of integration as float
        :param final_time: final time of integration as float
        :param min_length: minimum coil length as float
        :param max_length: maximum coil length as float
        :param mag_field_map: magnetic field winding map as dictionary
        :param f_division: integration numerical division as integer, default: 100
        """
        mag_field_down_list = []
        mag_field_up_list = []

        for winding_down in self.front_down_winding_numbers:
            mag_field_down_list.append(mag_field_map[winding_down])
        mag_field_down = max(mag_field_down_list)

        for winding_up in self.front_up_winding_numbers:
            mag_field_up_list.append(mag_field_map[winding_up])
        mag_field_up = max(mag_field_up_list)

        self.q_length_up = self.calculate_q_length(initial_time, final_time, mag_field=mag_field_up,
                                                   f_division=f_division, side="up")
        self.q_length_down = self.calculate_q_length(initial_time, final_time, mag_field=mag_field_down,
                                                     f_division=f_division, side="down")
        print(self.q_integrated_length_to_string())
        print(self.q_v_to_string())
        self.calculate_quench_front_position(self.q_length_down, self.q_length_up, min_length, max_length)
        self.convert_quench_front_to_nodes(self.coil_geometry)
        self.find_front_winding_numbers(self.coil_data)

    def calculate_q_length(self, initial_time, final_time, side, **kwargs):
        """
        Calculates quench front position after a given time by means of trapezoidal integration
        :param initial_time: initial time of integration as float
        :param final_time: final time of integration as float
        :param side: "down" or "up" as string
        :param kwargs: mag_field_map; magnetic field winding map as dictionary
        :param kwargs: f_division; integration numerical division as integer, default: 100
        :return: quench integration length as float
        """
        if initial_time > final_time:
            raise Exception("ERROR - final time should be larger than initial time; the results might be erroneous.")
        mag_field = kwargs["mag_field"]
        f_division = kwargs["f_division"]

        time_vector = np.linspace(initial_time, final_time, f_division)
        q_v_vector = []
        for i in range(len(time_vector)):
            q_v_vector.append(self.f_interpolation(time_vector[i], mag_field)[0][0])
        if side == "up":
            self.quench_velocity_up = q_v_vector[-1]
        elif side == "down":
            self.quench_velocity_down = q_v_vector[-1]
        else:
            raise ValueError("Wrong display of temporary quench velocity occurs!")
        integration_array = scipy.integrate.cumtrapz(q_v_vector, time_vector)
        integrated_q_length = integration_array[-1]
        return integrated_q_length