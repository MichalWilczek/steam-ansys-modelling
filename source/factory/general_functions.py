
import os
import numpy as np
import shutil

class GeneralFunctions(object):

    @staticmethod
    def check_if_object_exists(instance):
        try:
            instance
        except NameError:
            return False
        else:
            return True

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
    def remove_repetitive_values_from_list(mylist):
        """
        Removes repetitve values from list
        :param mylist: list
        :return: list without repetitions
        """
        return list(dict.fromkeys(mylist))

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

    @staticmethod
    def delete_file(filename, directory):
        """
        Deletes file in output_directory
        :param directory: analysis output_directory as string
        :param filename: filename to delete as string
        """
        path = os.path.join(directory, filename)
        if os.path.isfile(path):
            os.remove(path)
        else:
            print("Error: {} file not found".format(path))

    @staticmethod
    def make_python_wait_until_ansys_finishes(filename, directory, file_length=1):
        """
        Makes Python wait until process in ANSYS is finished
        :param directory:
        :param filename: filename as string given by ANSYS when it finishes processing
        :param file_length: number of rows in filename as integer
        """
        exists = False
        path = os.path.join(directory, filename)
        while exists is False:
            exists = os.path.isfile(path)
            if exists and GeneralFunctions.file_length(filename, analysis_directory=directory) == file_length:
                os.chdir(directory)
                with open('Process_Finished.txt', 'r') as f:
                    file_input = int(float(f.read()))
                if file_input == 1:
                    f.close()
                    break
                else:
                    exists = False
            else:
                exists = False

    @staticmethod
    def calculate_average_from_list(float_objects_in_list):
        """
        Returns the average of values given in the list
        :param float_objects_in_list: list of float values
        :return: average of input values
        """
        return sum(float_objects_in_list) / len(float_objects_in_list)

    @staticmethod
    def save_array(directory, filename, array):
        """
        Saves array as txt file
        :param directory: output_directory to save file as string
        :param filename: filename to be created as string
        :param array: array to be saved
        """
        path = os.path.join(directory, filename)
        np.savetxt(path, array)

    @staticmethod
    def load_file(directory, npoints, filename):
        """
        Loads file as numpy array if its number of rows corresponds to number of nodes in geometry
        :param directory: analysis output_directory as string
        :param npoints: number of nodes in defined geometry
        :param filename: filename as string, 'Temperature_Data.txt' set as default
        """
        loaded_file = None
        exists = False
        path = os.path.join(directory, filename)
        while exists is False:
            exists = os.path.isfile(path)
            if exists and GeneralFunctions.file_length(filename, analysis_directory=directory) == npoints:
                os.chdir(directory)
                loaded_file = np.loadtxt(path)
            else:
                exists = False
        return loaded_file

    @staticmethod
    def create_folder_in_directory(directory, foldername):
        """
        Creates a folder in the specified output_directory
        :param directory: output_directory as string
        :param foldername: folder to be created as string
        :return: final output_directory as string
        """
        os.chdir(directory)
        os.mkdir(foldername)
        return os.path.join(directory, foldername)

    @staticmethod
    def copy_object_to_another_object(directory_to_copy, directory_destination):
        """
        Copies the folder with its files to the specified output_directory
        :param directory_to_copy: as string
        :param directory_destination: as string
        """
        shutil.copytree(directory_to_copy, directory_destination)

    @staticmethod
    def write_line_to_file(directory, filename, input_value):
        path = os.path.join(directory, filename)
        os.chdir(directory)
        with open(path, "w") as file:
            file.write(input_value)
