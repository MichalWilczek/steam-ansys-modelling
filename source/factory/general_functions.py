
import os

class GeneralFunctions(object):

    @staticmethod
    def file_length(filename, analysis_directory):
        """
        :param filename: filename with extension as string
        :param analysis_directory: string
        :return: number of rows in a file as integer
        """
        os.chdir(analysis_directory)
        with open(filename) as myfile:
            return int(len(myfile.readlines()))

    @staticmethod
    def flatten_list(list_to_flatten):
        """
        Flattens list of list
        :param list_to_flatten: list of lists
        :return: list
        """
        flat_list = []
        for sublist in list_to_flatten:
            for item in sublist:
                flat_list.append(item)
        return flat_list

    @staticmethod
    def change_boolean_into_integer(boolean):
        """
        Changes boolean Python values to APDL language
        :param boolean: True or False
        :return: 1 or 0
        """
        if boolean:
            return 1
        else:
            return 0

    @staticmethod
    def check_if_string_is_float(name):
        """
        Checks whether the string is a hidden float number
        :param name: as string
        :return: boolean
        """
        try:
            float(name)
            return True
        except ValueError:
            return False


