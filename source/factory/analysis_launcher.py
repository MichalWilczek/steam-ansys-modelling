
import os
import shutil
import json
from collections import namedtuple
from source.factory.general_functions import GeneralFunctions

class AnalysisLauncher(GeneralFunctions):

    def __init__(self, directory):
        self.directory = directory
        self.output_directory = self.get_analysis_directory(directory)
        self.copy_input_files_to_output_directory()

    @staticmethod
    def get_analysis_directory(analysis_directory):
        """
        Creates analysis directory where output files will be stored
        :param analysis_directory: as string
        :return: output analysis data directory as string
        """
        output_directory = AnalysisLauncher.create_analysis_directories(analysis_directory)
        return output_directory

    def convert_json_to_class_object(self, class_name, json_filename):
        """
        Creates input data class from a json file
        :param class_name: class name as string
        :param json_filename: filename as string
        :return: created class
        """
        path = os.path.join(self.directory, 'input')
        os.chdir(path)
        if AnalysisLauncher.check_if_object_exists_in_directory(path, filename=json_filename):
            with open(json_filename) as json_file :
                data = json.load(json_file, object_hook=lambda d : namedtuple(class_name, d.keys())(*d.values()))
                return data
        else:
            raise ValueError("Please, create input .json file in input directory.")

    def copy_input_files_to_output_directory(self, output_copy_foldername="input_copy"):
        """
        Copies all input files used in the analysis to the output directory
        :param output_copy_foldername: copied input folder name as string
        """
        os.chdir(self.output_directory)
        input_directory = os.path.join(self.directory, "input")
        input_copy_directory = os.path.join(self.output_directory, output_copy_foldername)
        shutil.copytree(input_directory, input_copy_directory)

    @staticmethod
    def create_analysis_directories(analysis_directory, output_foldername="output", input_foldername="input"):
        """
        Creates the directory for the output files in the folder 'output'
        :param analysis_directory: analysis directory as string
        :param output_foldername: as string
        :param input_foldername: as string
        :return: directory for the output files as string
        """
        if not AnalysisLauncher.check_if_object_exists_in_directory(analysis_directory, input_foldername):
            raise ValueError("Please, create 'input' folder in specified analysis directory.")
        if not AnalysisLauncher.check_if_object_exists_in_directory(analysis_directory, output_foldername):
            AnalysisLauncher.create_folder_in_directory(analysis_directory, output_foldername)
        path = os.path.join(analysis_directory, output_foldername)
        last_analysis_folder = AnalysisLauncher.count_number_of_analysis_folders_in_directory(path)
        AnalysisLauncher.create_folder_in_directory(directory=path, foldername=str(last_analysis_folder+1))
        path_final = os.path.join(path, str(last_analysis_folder+1))
        return path_final

    @staticmethod
    def copy_object_to_another_object(directory_to_copy, directory_destination):
        """
        Copies the folder with its files to the specified directory
        :param directory_to_copy: as string
        :param directory_destination: as string
        """
        shutil.copytree(directory_to_copy, directory_destination)

    @staticmethod
    def check_if_object_exists_in_directory(directory, filename):
        """
        Checks whether the specified filename exists in the directory
        :param directory: directory as string
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
    def count_number_of_analysis_folders_in_directory(directory):
        """
        Returns the maximum folder number with hidden analyses in the analysis directory
        :param directory: directory as string
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

    @staticmethod
    def create_folder_in_directory(directory, foldername):
        """
        Creates a folder in the specified directory
        :param directory: directory as string
        :param foldername: folder to be created as string
        """
        os.chdir(directory)
        os.mkdir(foldername)
