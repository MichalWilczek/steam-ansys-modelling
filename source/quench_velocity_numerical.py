
from source.quench_velocity import QuenchFront
import numpy as np
import scipy.integrate


class QuenchFrontNum(QuenchFront):

    def __init__(self, x_down, x_up, label, **kwargs):
        QuenchFront.__init__(self, x_down, x_up, label)
        self.f_q_v = kwargs["q_v_interpolation_f"]

    def return_quench_front_position(self, initial_time, final_time, min_length, max_length, mag_field, f_division=200):
        q_length = self.calculate_q_length(initial_time, final_time, mag_field, f_division)
        self.calculate_quench_front_position(q_length, min_length, max_length)

    def calculate_q_length(self, initial_time, final_time, **kwargs):
        if initial_time > final_time:
            raise Exception("ERROR - final time should be larger than initial time; the results might be erroneous.")

        mag_field = kwargs["mag_field"]
        f_division = kwargs["f_division"]

        time_vector = np.linspace(initial_time, final_time, f_division)
        q_v_vector = []
        for i in range(len(time_vector)):
                q_v_vector.append(self.f_q_v(time_vector[i], mag_field)[0][0])
        integration_array = scipy.integrate.cumtrapz(q_v_vector, time_vector)
        integrated_q_length = integration_array[-1]

        return integrated_q_length
