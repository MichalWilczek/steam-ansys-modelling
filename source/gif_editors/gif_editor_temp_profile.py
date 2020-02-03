
import os
from source.post_processor.plots import Plots
from source.common_functions import general_functions
import matplotlib.pyplot as plt

Functions = general_functions.GeneralFunctions()
directory = "C:\\skew_quad_analysis\\output\\Case1\\temperature_profile_output"
directory_quench_state = "C:\\skew_quad_analysis\\output\\Case1\\quench_state_output"
number_files = 495
fig_files = []

load_quench_file = Functions.load_file(directory_quench_state, npoints=54289, filename="quench_state_1.txt")

duration = 0.05
os.chdir(directory)

for i in range(1, number_files+1):
    filename = "Temperature_Profile_" + str(i) + ".txt"
    array = Functions.load_file(directory, npoints=54289, filename=filename)
    array[:, 0] = load_quench_file[:, 0]
    fig = Plots.plot_quench_state(array)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel('L_coil, m')
    ax.set_ylabel('T, K')
    ax.set_ylim(top=50)
    ax.plot(array[:, 0], array[:, 1], linewidth=1.5)
    plt.grid(True)
    plt.show()
    Plots.save_quench_state_plot(fig=fig, iteration=i, filename="temp")
