
import math
import scipy.integrate
import numpy as np
from source.quench_velocity_map import QuenchVelocityMap
from source.quench_velocity_numerical import QuenchFrontNum

def ex_trapezoidal_integration(x):
        return 2.0 + math.cos(2.0 * math.sqrt(x))


no_spacings = 10
time_vector = np.linspace(0.0, 2.0, no_spacings)

f = np.linspace(0.0, 0.0, no_spacings)
for i in range(no_spacings):
        f[i] = ex_trapezoidal_integration(x=time_vector[i])

integral = scipy.integrate.cumtrapz(f, time_vector)
print(integral)

print("Hello")

Map = QuenchVelocityMap()
f_interpol = Map.f_interpolation
QF = QuenchFrontNum(x_down=100, x_up=150, label=1, q_v_interpolation_f=f_interpol)

q_length = QF.calculate_q_length(initial_time=0.14, final_time=0.18, mag_field=0.5)

print(q_length)