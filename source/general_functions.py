
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
        if boolean:
            return 1
        else:
            return 0





