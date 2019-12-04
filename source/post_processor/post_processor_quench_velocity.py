
from source.post_processor.post_processor import PostProcessor
from source.post_processor.quench_velocity.quench_merge import QuenchMerge
import numpy as np
import os

class PostProcessorQuenchVelocity(PostProcessor, QuenchMerge):

    def __init__(self, class_geometry, ansys_commands, v_quench, solver, input_data):
        PostProcessor.__init__(self, class_geometry, ansys_commands, v_quench, solver, input_data)

    def check_quench_state(self):
        self.check_quench_state_quench_velocity()

    def check_quench_state_quench_velocity(self):
        temperature_profile = self.temperature_profile
        quench_front_new = self.q_det.detect_quench(self.quench_fronts, temperature_profile,
                                                    magnetic_field_map=self.magnetic_map.im_short_mag_dict)
        for qf in quench_front_new:
            self.quench_fronts.append(self.qf(x_down=qf[0], x_up=qf[1], label=self.quench_label, factory=self.factory,
                                      class_geometry=self.geometry))
            self.quench_label += 1

    def estimate_coil_resistance(self):
        self.plot_resistive_voltage()

    def calculate_coil_resistance(self):
        coil_resistance = 0.0
        for qf in self.quench_fronts:
            quench_dict = self.geometry.retrieve_winding_numbers_and_quenched_nodes(
                x_down_node=qf.x_down_node, x_up_node=qf.x_up_node)
            for key in quench_dict:
                winding_number = int(float(key[7:]))
                mag_field = self.magnetic_map.im_short_mag_dict["winding" + str(winding_number)]
                n_down = quench_dict["winding" + str(winding_number)][0]
                n_up = quench_dict["winding" + str(winding_number)][1]
                qf_resistance = self.mat_props.calculate_qf_resistance(
                    qf_down=n_down, qf_up=n_up, im_temp_profile=self.temperature_profile,
                    im_coil_geom=self.geometry.coil_geometry, mag_field=mag_field,
                    wire_diameter=self.input_data.geometry_settings.type_input.strand_diameter)
                coil_resistance += qf_resistance
        return coil_resistance

    def plot_resistive_voltage(self):
        self.plot_ansys_resistive_voltage()
        self.plot_python_resistive_voltage(self.calculate_coil_resistance())

    def plot_ansys_resistive_voltage(self):
        time_step = [self.time_step_vector[self.iteration[0]]][0]
        resistive_voltage = self.geometry.load_ansys_output_one_line_txt_file(
            directory=self.directory, filename="Resistive_Voltage.txt")
        self.resistive_voltage = resistive_voltage
        self.plots.plot_resistive_voltage_ansys(voltage=abs(resistive_voltage),
                                                total_time=self.input_data.analysis_settings.time_total_simulation,
                                                time_step=time_step, iteration=self.iteration[0])

    def plot_python_resistive_voltage(self, coil_resistance):
        time_step = [self.time_step_vector[self.iteration[0]]][0]
        res_voltage = abs(self.circuit.return_current_in_time_step() * coil_resistance)
        self.plots.plot_resistive_voltage_python(voltage=res_voltage,
                                                 total_time=self.input_data.analysis_settings.time_total_simulation,
                                                 time_step=time_step,
                                                 iteration=self.iteration[0])
        res_voltage_array = np.zeros((1, 2))
        res_voltage_array[0, 0] = time_step
        res_voltage_array[0, 1] = res_voltage
        if self.iteration == 1:
            self.write_line_in_file(directory=self.plots.output_directory_resistive_voltage,
                                    filename="Res_Voltage.txt", mydata=res_voltage_array)
        else:
            self.write_line_in_file(directory=self.plots.output_directory_resistive_voltage,
                                    filename="Res_Voltage.txt", mydata=res_voltage_array,
                                    newfile=False)

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

    def update_magnetic_field(self):
        self.magnetic_map.update_magnetic_field_during_analysis(current=self.circuit.current[0])
