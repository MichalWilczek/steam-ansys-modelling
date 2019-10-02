
class ModelInput(object):

    @staticmethod
    def linear_time_stepping(time_division, total_time):
        """
        Returns at time vector for simulation with constant time step
        :param time_step: time step as float
        :param total_time: total simulation time as float
        :return: list of time steps
        """
        vector = []
        time_step = total_time/time_division
        for i in range(1, int(time_division)+1):
            vector.append(i*time_step)
        return vector

    @staticmethod
    def power_input_time_stepping(time_division, total_time, power_input_time=0.01, power_time_step=10.0):
        """
        Returns at time vector with initial time_step for power input
        :return:
        """
        linear_vector = ModelInput.linear_time_stepping(time_division, total_time)
        power_input_time_vector = []
        power_input_time_step = power_input_time/power_time_step
        for i in range(1, int(power_time_step)+1):
            power_input_time_vector.append(i*power_input_time_step)
        for j in range(len(linear_vector)):
            power_input_time_vector.append(power_input_time+linear_vector[j])
        return power_input_time_vector






