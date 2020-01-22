
from source.common_functions import general_functions
import numpy as np

Functions = general_functions.GeneralFunctions()

directory = "C:\\skew_quad_analysis\\hot_spot_case1"
filename_hot_spot = "hotspot.txt"
files_list = Functions.make_list_of_filenames_in_directory(directory)
hot_spot_array = np.zeros((len(files_list), 1))

for file in files_list:
    filename = file[:-3]
    filename = filename[20:]
    filename = int(float(filename))

    file_length = Functions.file_length(file, directory)
    file_content = Functions.load_file(directory, file_length, file)
    hot_spot = max(file_content[:, 1])
    hot_spot_array[filename-1, 0] = hot_spot

Functions.save_array(directory, filename_hot_spot, hot_spot_array)
