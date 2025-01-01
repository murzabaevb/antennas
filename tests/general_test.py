from controller import Antenna
from exporters.csv_export import CSVExport
from exporters.json_export import JSONExport
from exporters.yaml_export import YAMLExport
from exporters.msi_export import MSIExport


# Create an object of ITUF1336s Class (sectoral antenna)
my_antenna = Antenna('ITUF1336s')

# Set IMT BTS 1-3 GHz antenna parameters as per source [1]:
# https://www.itu.int/dms_pub/itu-r/opb/rep/r-rep-m.2292-2014-pdf-e.pdf
my_antenna.model.set_params(
    oper_freq_mhz=806,  # LTE Band 20 DL center frequency
    max_gain_dbi=15,  # [1] Table 2
    beamwidth_az_deg=65, # [1] Table 2
    pattern_type='average',  # [1] is neutral on this
    performance_type='improved',  # Ref. Rec. ITU-R F.1336-5
    tilt_type='electrical',  # [1] is silent on this
    tilt_angle_deg=3,  # [1] Table 2
    # beamwidth_el_deg= ,  # Auto calculated
    # k_p=0.7,  # not required for pattern_type='average'
    k_a=0.7,  # [1] Table 2
    k_h=0.7,  # [1] Table 2
    k_v=0.3,  # [1] Table 2
)

# Calculate antenna gain
print(f'G = {my_antenna.model.gain(azimuth=15.2, elevation=20.4):,.2f} dBi')

# Display antenna radiation patterns
my_antenna.model.show_patterns()

# Export antenna specs to files
my_csv_exporter = CSVExport()  # CSV exporter object
my_antenna.export(my_csv_exporter, 'f1336s_ant.csv')

my_json_exporter = JSONExport()  # JSON exporter object
my_antenna.export(my_json_exporter, 'f1336s_ant.json')

my_yaml_exporter = YAMLExport()  # YAML exporter object
my_antenna.export(my_yaml_exporter, 'f1336s_ant.yaml')

my_msi_exporter = MSIExport()  # MSI exporter object
my_antenna.export(my_msi_exporter, 'f1336s_ant.msi')

# Modify antenna to suite TETRA BTS 410-430 MHz as per source [2]
my_antenna.model.set_params(
    oper_freq_mhz=420,  # TETRA Band 0100 center frequency
    max_gain_dbi=15,  # Ref. to [2]
    beamwidth_az_deg=65, # Ref. to [2]
    beamwidth_el_deg=17, # Ref. to [2]
    pattern_type='average',  # [2] is silent on this
    performance_type='improved',  # R[2] is silent on this
    tilt_type='none',  # [1] is neutral on this
)

# Display radiation patterns of modified antenna
my_antenna.model.show_patterns()

# Delete antenna object
del my_antenna

# Create an object of ITUF699 Class (microwave link)
my_antenna = Antenna('ITUF699')

# Set antenna's parameters as per [2]
# https://www.itu.int/dms_pubrec/itu-r/rec/f/R-REC-F.758-7-201911-I!!PDF-E.pdf
my_antenna.model.set_params(
    oper_freq_mhz=26875,  # Middle frequency of the range
    max_gain_dbi=48,  # [2] Table 9
)

# Calculate antenna gain
print(f'G = {my_antenna.model.gain(off_axis_angle=15.2):,.2f} dBi')

# Display antenna radiation patterns
my_antenna.model.show_patterns()

# Export the radiation patterns to MSI file
my_antenna.export(my_msi_exporter, '../exports/f699_ant.msi')

# Delete antenna object
del my_antenna

# Create an object of ITUF1245 Class (microwave link)
my_antenna = Antenna('ITUF1245')

# Set antenna's parameters as per [2]
my_antenna.model.set_params(
    oper_freq_mhz=26875,  # Middle frequency of the range
    calc_opt='Rec. 2',  # Average patterns as per Recommends 2
    max_gain_dbi=48,  # [2] Table 9
)

# Calculate antenna gain
print(f'G = {my_antenna.model.gain(off_axis_angle=15.2):,.2f} dBi')

# Display antenna radiation patterns
my_antenna.model.show_patterns()

# Export the radiation patterns to MSI file
my_antenna.export(my_msi_exporter, '../exports/f1245_ant.msi')

# Modify antenna settings to suite specs provided below based on max. gain
# https://www.commscope.com/globalassets/digizuite/957219-p360-usx6-3-4wh-external.pdf
my_antenna.model.set_params(
    oper_freq_mhz=3900,  # Middle frequency; specs sheet
    calc_opt='Rec. 2',  # Average patterns as per Recommends 2
    max_gain_dbi=34.8,  # Specs sheet
)

# Display antenna radiation patterns
my_antenna.model.show_patterns()

# Modify antenna settings to use antenna diameter instead of max. gain
# https://www.commscope.com/globalassets/digizuite/957219-p360-usx6-3-4wh-external.pdf
my_antenna.model.set_params(
    oper_freq_mhz=3900,  # Middle frequency; specs sheet
    calc_opt='Rec. 2',  # Average patterns as per Recommends 2
    diameter_m=1.8,  # Specs sheet
)

# Display antenna radiation patterns
my_antenna.model.show_patterns()

# Delete antenna object
del my_antenna