
import os
import shutil
import json
import time
from collections import namedtuple
from source.factory.general_functions import GeneralFunctions

class AnalysisLauncher(GeneralFunctions):

    def __init__(self, input_data, json_directory, json_filename):
        self.json_filename = json_filename
        self.input_directory = json_directory
        self.directory = input_data.analysis_output_directory
        self.output_directory = AnalysisLauncher.get_output_directory(self.directory)
        self.input_copy_directory = self.copy_input_json_file_to_output_directory()

    @staticmethod
    def get_output_directory(analysis_directory):
        """
        Creates analysis output_directory where output files will be stored
        :param analysis_directory: as string
        :return: output analysis data output_directory as string
        """
        output_directory = AnalysisLauncher.create_analysis_output_directories(analysis_directory)
        return output_directory

    @staticmethod
    def convert_json_to_class_object(json_filename, json_filename_directory, class_name="InputUser"):
        """
        Creates input data Class from a json file
        :param json_filename: as string
        :param json_filename_directory: as string
        :param class_name: as string, default: 'InputUser'
        :return: Class with all input data from json file
        """
        if AnalysisLauncher.check_if_object_exists_in_directory(json_filename_directory, filename=json_filename):
            with open(json_filename) as json_file:
                data = json.load(json_file, object_hook=lambda d: namedtuple(class_name, d.keys())(*d.values()))
                return data
        else:
            raise ValueError(".json input file does not exist in specified directory.")

    def copy_input_json_file_to_output_directory(self):
        """
        Copies all input files used in the analysis to the output output_directory
        :return: directory with copied input files as string
        """
        os.chdir(self.output_directory)
        input_copy_directory = GeneralFunctions.create_folder_in_directory(
            directory=self.output_directory, foldername="input_copy")
        input_json_file_directory = os.path.join(self.input_directory, self.json_filename)
        shutil.copy(input_json_file_directory, input_copy_directory)
        return input_copy_directory

    @staticmethod
    def create_analysis_output_directories(analysis_directory):
        """
        Creates the output_directory for the output files in the folder 'output'
        :param analysis_directory: analysis directory as string
        :return: output_directory for the output files as string
        """
        last_analysis_folder = AnalysisLauncher.count_number_of_analysis_output_folders_in_directory(analysis_directory)
        AnalysisLauncher.create_folder_in_directory(
            directory=analysis_directory, foldername=str(last_analysis_folder+1))
        path_final = os.path.join(analysis_directory, str(last_analysis_folder+1))
        return path_final

    def copy_ansys_analysis_files_to_output_results_directory(self):
        """
        Cuts the ANSYS files from the ANSYS initial directory and pastes them to the final output directory specified
        by the user
        """
        time.sleep(2)
        list_files = os.listdir(self.directory)
        for file in list_files:
            path = os.path.join(self.directory, file)
            if os.path.isfile(path):
                shutil.copy(path, self.output_directory)
                GeneralFunctions.delete_file(file, self.directory)

    @staticmethod
    def check_if_object_exists_in_directory(directory, filename):
        """
        Checks whether the specified filename exists in the output_directory
        :param directory: output_directory as string
        :param filename: filename as string
        :return: boolean
        """
        os.chdir(directory)
        list_files = os.listdir(directory)
        if filename in list_files:
            return True
        else:
            return False

    @staticmethod
    def count_number_of_analysis_output_folders_in_directory(directory):
        """
        Returns the maximum folder number with hidden analyses in the analysis output_directory
        :param directory: output_directory as string
        :return: folder number as integer
        """
        os.chdir(directory)
        list_files = os.listdir(directory)
        list_folders = []
        for name in list_files:
            if GeneralFunctions.check_if_string_is_float(name):
                name_int = int(float(name))
                list_folders.append(name_int)
        list_folders.sort()
        if len(list_folders) == 0:
            return 0
        else:
            return list_folders[-1]
