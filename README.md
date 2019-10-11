## **STEAM** 
#### 3D Quench Velocity Modelling in ANSYS
(Copyright © 2019, CERN, Switzerland. All rights reserved.)

## Prerequisites
In order to run the script, the user should have the installed version of ANSYS APDL.

##### Initial Simulation Settings
The first part of configuration corresponds to definition of basic simulation settings. 
```json
{"analysis_settings": {
    "quench_init_position": 0.5,
    "quench_init_length": 0.1,
    "time_total_simulation": 0.4,
    "time_step_cosimulation": 0.01,
    "time_step_min_ansys": 1.0,
    "time_step_max_ansys": 10.0,
    "current_init": 100.0
    }}
```
Analysis settings definition is composed of:

 Argument | Units | Description 
 -------- | ----- | ----------- 
quench_init_position | m | Position of the centre of the initially quenched zone.
quench_init_length | m | Length of the initially quenched zone.
time_total_simulation | s | Total simulation time.
time_step_cosimulation | s | Time step after each of which the data is extracted from ANSYS. It is also a time slot for data exchange between ANSYS and quench velocity algorithm.
time_step_min_ansys | ms | Minimum time step applied within the automatic ANSYS time stepping algorithm. It must be smaller than the time_step_cosimulation.
time_step_max_ansys | ms | Maximum time step applied within the automatic ANSYS time stepping algorithm. It must be smaller than the time_step_cosimulation.
current_init | A | Initial current set in the analysis.

##### Temperature Distribution Settings
The user should decide what what type of temperature conditions will be applied in the analysis. 
```json
{"temperature_init_distribution": {
	"type": "gaussian",
	"input": {
		"temperature_init": 1.9, 
		"temperature_max_init_quenched_zone": 10.0, 
		"magnetic_field_initially_quenched_winding": 2.0}	
}}
```
There are two different types available: uniform and gaussian. Each of them requires different input as described below: 

 Type | Required Input 
 ---- | --------------
 gaussian | temperature_init, temperature_max_init_quenched_zone
 uniform | temperature_init, temperature_max_init_quenched_zone, magnetic_field_initially_quenched_winding

Temperature distribution settings is composed of:

 Argument | Units | Description 
 -------- | ----- | ----------- 
 temperature_init | K | Initial temperature set outside of the initially quenched zone.
 temperature_max_init_quenched_zone | K | Maximum temperature set in the quenched zone.
 magnetic_field_initially_quenched_winding | T | Magnetic field value in the winding where the initial quench is triggered. This value is only required for the initial gaussian distribution whose borders of the quenched zone are at critical temperature dependent on the magnetic field strength.

##### Analysis Type Settings
The programme is written in order to perform one- and multi-dimensional analysis based on quench velocity algorithm. However, it is also possible 
to conduct one-dimensional heat-balance equation-based analyses for mapping purposed. Therefore, the user should define the type
of analysis to be carried out.
specified as follows:
```json
{"analysis_type": {
	"type": "quench_velocity",
	"input": {
		"v_quench_model": "numerical"}
		}
}
```
There are two different types available: quench_velocity and heat_balance. Each of them requires different input as described below: 

 Type | Required Input 
 ---- | --------------
 quench_velocity | v_quench_model
 heat_balance | -

The analysis type input settings is presented below:

 v_quench_model argument  | Description 
 --------  | ----------- 
 constant | Applies constant quench velocity.
 numerical | Initial temperature set outside of the initially quenched zone.

The user options for the analysis of the electric circuit
```json
{"circuit_settings": {
    "build_electric_circuit": false,
    "input": {"transient_electric_analysis": false}
	}
}
```

##### Material Properties Settings
Material properties settings definition is composed of:

 Argument | Units | Type | Description 
 -------- | ----- | ---- | ----------- 
 nonsupercond_to_supercond_ratio | - | linear, nonlinear | Non-superconductor to superconductor ratio 
 rrr | - | nonlinear |Residual resistivity ratio of the normal conductor 
 min_temperature_property | K | linear, nonlinear | Minimum temperature of material properties in ANSYS 
 max_temperature_property | K | linear, nonlinear | Maximum temperature of material properties in ANSYS 
 superconductor_name | - | nonlinear | Superconductor name, only works for 'Nb-Ti' 
 normal_conductor_name | - | nonlinear | Normal conductor name, only works for 'Cu'
 insulation_name | - | nonlinear | Insulation name, only works for 'G10'
 txt_data_output | - | linear, nonlinear | Specifies whether txt files with material properties should be saved
 png_data_output | - | linear, nonlinear | Specifies whether png files with material properties should be saved
 magnetic_field_value_list | T | nonlinear | Specifies at what magnetic field values the material property should be evaluated for saving 
 

 
 



The user should choose material properties
```json
{"material_properties_settings": {
    "type": "nonlinear",
    "input": {
        "f_cu_f_nbti": 2.2, 
        "rrr": 193.0}
	}
}
```

The user magnetic field
```json
{"magnetic_field_settings": {
	"magnetic_map_model": "2D_static",
	"input": {"magnetic_field_map_plot": false}
	}
}
```

##### Geometry Settings
At the moment, the programme works for two types of geometries: skew quadrupole and so called "slab" which is a 1D cable 
domain of a rectangular shape. Both geometries can consist of one winding (dimensionality: "1D") or multiple windings (dimensionality: "multiple_1D").
The exemplary variable input for a multiple_1D skew quadrupole geometry is presented below.
```json
{"geometry_settings": {
	"geometry_type": {
		"type": "skew_quadrupole",
		"dimensionality": "multiple_1D",
		"type_input": {
            "strand_diameter": 0.7, 
            "winding_side": 0.941, 
            "coil_long_side": 413.21, 
            "coil_short_side": 126.81, 
            "coil_initial_radius": 9.15, 
            "number_turns_in_layer": 29,
            "insulation_analysis": true,
            "winding_number_first_in_analysis": 233,
            "winding_number_last_in_first_layer": 234,
            "number_of_layers_in_analysis": 2},
        "mesh_input": {
            "division_long_side": 100, 
            "division_short_side": 30, 
            "division_radius": 5},
        "dimensionality_input": {}
		}
	}
}
```
Common type_input for "slab" and "skew_quadrupole":

 Argument, type_input | Units | Description 
 -------------------- | ----- | ----------- 
 strand_diameter | mm | 
 winding_side | mm | 
 number_turns_in_layer | - | 
 number_layers | - |
 
type_input only for "skew_quadrupole" geometry:

 Argument, type_input | Units | Description 
 -------------------- | ----- | ----------- 
 coil_long_side | mm | 
 coil_short_side | mm |
 coil_initial_radius | mm |
 winding_number_first_in_analysis | - |
 winding_number_last_in_first_layer | - | 
 number_of_layers_in_analysis | - | 
 
type_input only for "slab" geometry:

 Argument, type_input | Units | Description 
 -------------------- | ----- | ----------- 
 length_per_winding | m | 
 
 Argument, mesh_input | Units | Description | type_input
 -------------------- | ----- | ----------- | ----------
 division_long_side | - | Number of elements along the longer side of skew quadrupole. | skew_quadrupole
 division_short_side | - | Number of elements along the shorter side of the skew quadrupole. | skew_quadrupole
 divisions_radius | - | Number of elements along the winding arc of the skew quadrupole. | skew_quadrupole
 division_per_winding | - | Number of elements along the 1D slab cable | slab
