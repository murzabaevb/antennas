from controller import Antenna

# Create an object of ITUF1336s Class (sectoral antenna)
my_antenna = Antenna('ITUF1336s')

# Set IMT BTS 3-6 GHz antenna parameters as per source [1]:
# https://www.itu.int/dms_pub/itu-r/opb/rep/r-rep-m.2292-2014-pdf-e.pdf
my_antenna.model.set_params(
    oper_freq_mhz=3550,  # NR Band n78 TD3500 center frequency
    max_gain_dbi=18,  # [1] Table 4
    beamwidth_az_deg=65, # [1] Table 4
    pattern_type='average',  # [1] is neutral on this
    performance_type='improved',  # Ref. Rec. ITU-R F.1336-5
    tilt_type='mechanical',  # [1] is silent on this
    tilt_angle_deg=6,  # [1] Table 4
    # beamwidth_el_deg= ,  # Auto calculated
    k_p=0.7,  # [1] Table 4
    k_a=0.7,  # [1] Table 4
    k_h=0.7,  # [1] Table 4
    k_v=0.3,  # [1] Table 4
)

# Calculate antenna gain
print(f'G = {my_antenna.model.gain(azimuth=15.2, elevation=20.4):,.2f} dBi')

# Display antenna radiation patterns
my_antenna.model.show_patterns()