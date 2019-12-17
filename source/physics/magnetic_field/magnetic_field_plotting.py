
import matplotlib as mpl
import matplotlib.pyplot as plt
from source.common_functions.general_functions import GeneralFunctions
import numpy as np

class MagneticFieldPlotting(object):

    @staticmethod
    def plot_mag_field_in_windings(x_vector, y_vector, b_field_vector, discretisation_number=51):
        discretisation_array = np.linspace(0, 1, discretisation_number)
        discrete_colors = plt.cm.jet(discretisation_array)

        cmap = plt.get_cmap('jet', discretisation_number)
        Vmin = b_field_vector.min()
        Vmax = b_field_vector.max()
        Vrange = np.absolute(Vmax - Vmin)
        color_vector = (b_field_vector - Vmin) / Vrange

        norm = mpl.colors.Normalize(vmin=Vmin, vmax=Vmax)
        discrete_color_vector = []
        for x in np.nditer(color_vector):
            discrete_color_vector.append(GeneralFunctions.find_nearest_in_numpy_array(discretisation_array, x))

        discrete_color_vector = np.array(discrete_color_vector)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('x-direction, m')
        ax.set_ylabel('y-direction, m')
        for i in range(np.size(x_vector)):
            ax.plot(x_vector[i], y_vector[i], 'o', markersize=4,
                    color=discrete_colors[int(np.where(discretisation_array == discrete_color_vector[i])[0])])
        plt.axis('equal')
        plt.grid(True)

        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        fig.colorbar(sm, ticks=np.linspace(Vmin, Vmax, int(discretisation_number / 5)),
                     boundaries=np.arange(Vmin - Vrange * 0.05, Vmax + Vrange * 0.05, Vrange/10),
                     label='Magnetic Field [T]')
        plt.show()
