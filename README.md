## **STEAM** 
#### ANSYS Quench Velocity Modelling
(Copyright © 2019, CERN, Switzerland. All rights reserved.)

## Prerequisites
In order to run the script, the user should have the installed version of ANSYS APDL

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
| Argument | Units | Description |
| -------- | ----- | ----------- |





	
The user should also decide what what type of temperature conditions will be applied in the analysis.	
```json
{"temperature_init_distribution": {
	"type": "gaussian",
	"input": {
		"temperature_init": 1.9, 
		"temperature_max_init_quenched_zone": 10.0, 
		"magnetic_field_initially_quenched_winding": 2.0}	
}}
```

Analysis type
```json
{"analysis_type": {
	"type": "quench_velocity",
	"input": {
		"v_quench_model": "numerical", 
		"electric_ansys_elements": true}
		}
}
```

The user the options for the analysis of the electric circuit
```json
{"circuit_settings": {
    "build_electric_circuit": false,
    "input": {"transient_electric_analysis": false}
	}
}
```

The user should choose material properties
```json
{"material_properties_settings": {
    "type": "nonlinear",
    "input": {
        "f_cu_f_nbti": 2.2, 
        "rrr": 193.0, 
        "material_properties_directory": "C:\\gitlab\\steam-ansys-modelling\\Material_Properties"}
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

The user should define geometry creation...
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


