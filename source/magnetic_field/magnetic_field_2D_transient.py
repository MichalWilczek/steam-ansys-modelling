
from source.magnetic_field.magnetic_field_map import MagneticFieldMap
from source.magnetic_field.winding_remap import WindingRemap


class MagneticField2DTransient(MagneticFieldMap, WindingRemap):

    def __init__(self, input_data):
        WindingRemap.__init__(self, input_data=input_data)




