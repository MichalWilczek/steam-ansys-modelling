
import os
from source.post_processor.plots import Plots
from source.common_functions import general_functions

Functions = general_functions.GeneralFunctions()
directory = "C:\\skew_quad_analysis\\output\\Case1\\quench_state_output"
number_files = 476
fig_files = []

duration = 0.05
os.chdir(directory)

for i in range(1, number_files+1):
    filename = "quench_state_" + str(i) + ".txt"
    array = Functions.load_file_ansys(directory, npoints=54289, filename=filename)
    fig = Plots.plot_quench_state(array)
    Plots.save_quench_state_plot(fig=fig, iteration=i, filename="quench")

