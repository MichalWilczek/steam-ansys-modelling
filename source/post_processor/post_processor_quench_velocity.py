
from source.post_processor.post_processor import PostProcessor
from source.physics.quench_velocity.quench_merge import QuenchMerge
import numpy as np
import os

class PostProcessorQuenchVelocity(PostProcessor):

    def __init__(self, class_geometry, ansys_commands, v_quench, solver, input_data):
        PostProcessor.__init__(self, class_geometry, ansys_commands, v_quench, solver, input_data)

    def check_quench_state(self):
        self.check_quench_state_quench_velocity()

    def check_quench_state_quench_velocity(self):
        temperature_profile = self.temperature_profile
        quench_fronts_new = self.q_det.detect_quench(self.quench_fronts, temperature_profile,
                                                     magnetic_field_map=self.magnetic_map.im_short_mag_dict)
        self.quench_fronts_new = []
        for qf in quench_fronts_new:
            self.quench_fronts_new.append(self.qf(x_down=qf[0], x_up=qf[1],
                                                  label=self.quench_label,
                                                  factory=self.factory,
                                                  class_geometry=self.geometry))
            self.quench_label += 1
        self.quench_fronts.extend(self.quench_fronts_new)

    def estimate_resistive_voltage(self):
        self.resistive_voltage = self.calculate_resistive_voltage()
        self.write_down_resistive_voltage_to_file(self.resistive_voltage)
        self.plot_resistive_voltage()

    def calculate_resistive_voltage(self):
        return self.geometry.load_ansys_output_one_line_txt_file(
            directory=self.directory, filename="Resistive_Voltage.txt")

    def estimate_quench_velocity(self):
        magnetic_map = self.magnetic_map.im_short_mag_dict

        # calculate quench propagation
        for qf in self.quench_fronts:
            qf.return_quench_front_position(
                initial_time=self.time_step_vector[self.iteration[0]-1],
                final_time=self.time_step_vector[self.iteration[0]],
                min_length=self.min_coil_length,
                max_length=self.max_coil_length,
                mag_field_map=magnetic_map,
                current=self.circuit.current[0])

        # what if quench fronts meet
        self.quench_fronts = QuenchMerge.quench_merge(self.quench_fronts)

    def get_current(self):
        path = os.path.join(self.directory, "sol_dump_resistor.inp")
        with open(path) as myfile:
            number_lines = int(len(myfile.readlines()))
        dump_resistor_current_voltage_power = np.loadtxt(path, skiprows=number_lines-1, max_rows=1, usecols=(1, 2))
        self.circuit.current[0] = abs(dump_resistor_current_voltage_power[0])
        self.circuit.check_if_magnet_is_discharged()

    def update_magnetic_field(self):
        self.magnetic_map.update_magnetic_field_during_analysis(current=self.circuit.current[0])
