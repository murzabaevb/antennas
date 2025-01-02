"""
References:
1.  "Rec. ITU-R F.1336-5. Reference radiation patterns of
    omnidirectional, sectoral and other antennas for the fixed
    and mobile services for use in sharing studies in the
    frequency range from 400 MHz to about 70 GHz"
"""


import math
from base import BaseAntenna


class ITUF1336lg(BaseAntenna):
    """ITU-R F.1336-5 ow-gain Antenna Model."""
    def __init__(self):
        super().__init__()

    PARAMS = {
        # Operating frequency (MHz)
        'oper_freq_mhz': {
            'category': 'mandatory',
            'type': (int, float),
            'range': (1000, 3000),
        },

        # Maximum main-lobe antenna gain (dBi)
        'max_gain_dbi': {
            'category': 'mandatory',
            'type': (int, float),
            'range': (-29.9, 20),
        },
    }


    def _post_set_params(self):
        """Set dependent and not set optional parameters.

        This method runs after set_params() of the superclass.
        """
        pass  # done intentionally, i.e. not needed


    def _update_specs(self):
        """Update specs data."""
        # Indicate all parameters used in the modeling in comment
        comment_str = ''  # left intentionally empty

        self.specs["name"] = 'ITU-R F.1336-5 Low-Gain'
        self.specs['make'] = 'ITU'
        self.specs['frequency'] = self.params['oper_freq_mhz']
        # Calculate 3 dB beamwidth in azimuth and elevation planes
        g_0 = self.params['max_gain_dbi']
        phi_3 = math.sqrt(27000 * 10**(-0.1 * g_0))
        self.specs['h_width'] = round(phi_3, 2)
        self.specs['v_width'] = round(phi_3, 2)  # same as for h_width
        self.specs['front_to_back'] = 'n/a'
        self.specs['gain']  = self.params['max_gain_dbi']
        self.specs['tilt'] = 0
        self.specs['polarization'] = 'n/a'
        self.specs['comment'] = comment_str

        # Generate angles from 0 to 360 (inclusive)
        angles = [i for i in range(0, 361)]

        # Create empty lists for h_loss
        h_loss = []

        g_max = self.params['max_gain_dbi']  # for attenuation calc.

        # Calculate h_loss array's values
        for angle in angles:
            # calc. gain, then attenuation, then append
            h_loss.append(round(g_max - self.gain(off_axis_angle=angle), 2))

        # Make v_loss the same as h_loss
        v_loss = h_loss

        # Complete specs dict. with angle/loss data
        self.specs['h_pattern_datapoint']['phi'] = angles
        self.specs['h_pattern_datapoint']['loss'] = h_loss

        self.specs['v_pattern_datapoint']['theta'] = angles
        self.specs['v_pattern_datapoint']['loss'] = v_loss


    def gain(self, **kwargs):
        """Compute antenna gain (dBi) at given off-axis angle.

        Only for the case of peak side-lobe patterns in 1-3 GHz
        frequency range, circular symmetry about the 3 dB beamwidth
        and with a main lobe antenna gain less than about 20 dBi.

        Keyword Args
        ------------
        off_axis_angle (int or float) :
            Off-axis angle (degrees) (0 <= off_axis_angle <= 180)

        Returns
        -------
        int or float
            Antenna gain (dBi) at given off-axis angle

        Notes
        -----
        Refer to [1] Recommends 4
        """

        # Define expected keys and their types
        required_keys = {
            "off_axis_angle": (int, float),  # Accept int or float for azimuth
        }

        # Check if all required keys are present
        for key in required_keys:
            if key not in kwargs:
                raise KeyError(f"Missing required key: '{key}'")

        # Validate the type of each provided value
        for key, expected_types in required_keys.items():
            value = kwargs[key]
            if not isinstance(value, expected_types):
                raise TypeError(f"Key '{key}' must be of type {expected_types}, got {type(value).__name__}")

        # If validation passes, assign values to variables
        theta = kwargs['off_axis_angle']

        # Bring the angle to expected ranges
        theta = self.__normalize_off_axis_angle(theta)

        g_0 = self.params['max_gain_dbi']
        phi_3 = math.sqrt(27000 * 10**(-0.1 * g_0))
        phi_1 = 1.9 * phi_3
        phi_2 = phi_1 * 10**((g_0 - 6) / 32)

        if 0 <= theta < (1.08 * phi_3):
            return g_0 - 12 * (theta / phi_3)**2
        elif (1.08 * phi_3) <= theta < phi_1:
            return g_0 - 14
        elif phi_1 <= theta < phi_2:
            return g_0 - 14 - 32 * math.log10(theta / phi_1)
        elif phi_2 <= theta <= 180:
            return -8


    @staticmethod
    def __normalize_off_axis_angle(angle):
        """Normalize angle to be between 0 and +180 degrees.

        Parameters
        ----------
        angle : int or float
            off-axis angle (degrees)

        Returns
        -------
        int or float
            Azimuth angle (degrees) between 0 and +180
        """
        angle = (angle % 360 + 360) % 360  # Wrap angle to [0, 360]
        if angle > 180:
            angle = 360 - angle  # Mirror to [0, 180]
        return angle
