from controller import Antenna
from exporters.msi_export import MSIExport

# Create antenna Object using ITUS465
my_antenna = Antenna('ITUS465')

# # Set antenna parameters
# my_antenna.model.set_params(
#     oper_freq_mhz=2000,
#     d_to_l=30,
# )

# Set antenna parameters
my_antenna.model.set_params(
    oper_freq_mhz=2000,
    diameter_m=0.3,
)

# Calculate the gain
#print(f"G={my_antenna.model.gain(off_axis_angle=3):,.2f} dBi")
print(my_antenna.model.gain(off_axis_angle=180))

# Issue with when gain() returns None to be solved for show_patterns()
my_antenna.model.show_patterns()

# Export antenna specs to files
my_msi_exporter = MSIExport()  # MSI exporter object
my_antenna.export(my_msi_exporter, 's465_ant.msi')