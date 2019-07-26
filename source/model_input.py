
from source.factory import AnalysisBuilder

class ModelInput:

    @staticmethod
    def linear_time_stepping(time_division=AnalysisBuilder().get_time_division(),
                             total_time=AnalysisBuilder().get_total_time()):
        """
        Returns at time vector for simulation with constant time step
        :param time_step: time step as float
        :param total_time: total simulation time as float
        :return: list of time steps
        """
        vector = []
        i = total_time/time_division
        while i <= total_time:
            vector.append(i)
            i += total_time/time_division
        return vector
