
class TimeStep(object):

    @staticmethod
    def linear_time_stepping(time_step, total_time):
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
        time_step_digits = TimeStep.check_number_of_digits_behind_comma(time_step)
        vector.append(0.0)
        while i < total_time:
            vector.append(round(i, time_step_digits))
            i += time_step
            if i >= total_time:
                vector.append(total_time)
        print(TimeStep.time_step_vector_to_string(vector))
        return vector

    @staticmethod
    def check_number_of_digits_behind_comma(float_number):
        comma_index = str(float_number).find('.')
        number_digits = len(str(float_number)[comma_index:])-1
        return number_digits

    @staticmethod
    def time_step_vector_to_string(time_step_vector):
        return "The current time step vector is: {}".format(time_step_vector)

    # @staticmethod
    # def power_input_time_stepping(time_division, total_time, power_input_time=0.01, power_time_step=10.0):
    #     """
    #     Returns at time vector with initial time_step for power input
    #     :return:
    #     """
    #     linear_vector = TimeStep.linear_time_stepping(time_division, total_time)
    #     power_input_time_vector = []
    #     power_input_time_step = power_input_time/power_time_step
    #     for i in range(1, int(power_time_step)+1):
    #         power_input_time_vector.append(i*power_input_time_step)
    #     for j in range(len(linear_vector)):
    #         power_input_time_vector.append(power_input_time+linear_vector[j])
    #     return power_input_time_vector


