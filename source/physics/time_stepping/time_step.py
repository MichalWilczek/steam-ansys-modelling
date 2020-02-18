
from source.common_functions.general_functions import GeneralFunctions

class TimeStep(object):

    @staticmethod
    def time_step_vector_to_string(time_step_vector):
        return "The current time step vector is: {}".format(time_step_vector)

    @staticmethod
    def create_initial_time_step_vector(time_step, total_time):
        """
        Returns at time vector for simulation with constant time step
        :param time_step: time step as float
        :param total_time: total simulation time as float
        :return: list of time steps
        """
        if type(time_step) != float or type(total_time) != float:
            raise TypeError("Time step and total time should be float numbers !!!")
        vector = []
        i = time_step
        time_step_digits = GeneralFunctions.check_number_of_digits_behind_comma(time_step)
        vector.append(0.0)
        while i <= total_time:
            vector.append(round(i, time_step_digits))
            i += time_step
            if i >= total_time:
                vector.append(total_time)
        vector = GeneralFunctions.remove_repetitive_values_from_list(vector)
        print(TimeStep.time_step_vector_to_string(vector))
        return vector


