"""
References:
1.  "Rec. ITU-R F.1336-5. Reference radiation patterns of
    omnidirectional, sectoral and other antennas for the fixed
    and mobile services for use in sharing studies in the
    frequency range from 400 MHz to about 70 GHz"
"""


import math
from antenna.base import BaseAntenna


class ITUF1336o(BaseAntenna):
    """ITU-F.1336-5 Omnidirectional Antenna Model."""
    def __init__(self):
        super().__init__()

    PARAMS = {
        # Operating frequency (MHz)
        'oper_freq_mhz': {
            'category': 'mandatory',
            'type': (int, float),
            'range': (400, 70000),
        },

        # Maximum main-lobe antenna gain (dBi)
        'max_gain_dbi': {
            'category': 'mandatory',
            'type': (int, float),
            'range': (-29.9, 59.9),
        },

        # Side-lobe pattern type
        'pattern_type': {
            'category': 'mandatory',
            'type': str,
            'allowed': ['average', 'peak'],
        },

        # Side-lobe performance type.
        'performance_type': {
            'category': 'mandatory',
            'type': str,
            'allowed': ['typical', 'improved'],
        },

        # Downward tilt type.
        'tilt_type': {
            'category': 'mandatory',
            'type': str,
            'allowed': ['none', 'electrical'],
        },

        # Downward tilt angle (degrees).
        # Angles below horizontal plane are positive.
        'tilt_angle_deg': {
            'category': 'conditional',
            'type': (int, float),
            'range': (-89.9, 89.9),
            'depends_on': {'tilt_type': lambda x: x != 'none'},
        },

        # 3dB beamwidth (degrees) in the elevation plane.
        'beamwidth_el_deg': {
            'category': 'optional',
            'type': (int, float),
            'range': (0.1, 179.9),
        },

        # Parameter that accounts for increased side-lobe levels
        # k=0.7 for typical side-lobe performance; k=0 for improved.
        'k': {
            'category': 'optional',
            'type': float,
            'range': (0.001, 0.999),
        },
    }


    def _post_set_params(self):
        """Set dependent and not set optional parameters.

        This method runs after set_params() of the superclass.
        """
        # Set 3dB beamwidth in elevation plane is not provided
        if self.params.get('beamwidth_el_deg') is None:
            # Ref to [1] Formula (23b)
            g_0 = self.params['max_gain_dbi']
            self.params['beamwidth_el_deg'] = 107.6 * 10 ** (-0.1 * g_0)

        # Set downward tilt angle (degrees) if not set
        if (self.params.get('tilt_angle_deg') is None
                or self.params['tilt_type'] == 'none'):
            self.params['tilt_angle_deg'] = 0

        # Set k-factor if not set
        if self.params.get('k') is None:
            if (self.params['performance_type'] == 'typical'
                    and self.params['oper_freq_mhz'] <= 3000):
                self.params['k'] = 0.7 # Ref. to [1] Recommends 2.3
            else:
                self.params['k'] = 0  # Ref. to [1] Recommends 2.4


    def _update_specs(self):
        """Update specs data."""
        # Indicate all parameters used in the modeling in comment
        comment_str = (
            f'Side-lobe: '
            f'{self.params['pattern_type']}/'
            f'{self.params['performance_type']}, '
            f'tilting: {self.params['tilt_type']}, '
            f'k={self.params['k']}'
        )

        self.specs["name"] = 'ITU-R F.1336-5 Omnidirectional'
        self.specs['make'] = 'ITU'
        self.specs['frequency'] = self.params['oper_freq_mhz']
        self.specs['h_width'] = 360
        self.specs['v_width'] = round(self.params['beamwidth_el_deg'], 2)
        self.specs['front_to_back'] = 'n/a'
        self.specs['gain'] = self.params['max_gain_dbi']
        self.specs['tilt'] = self.params['tilt_angle_deg']
        self.specs['polarization'] = 'n/a'
        self.specs['comment'] = comment_str

        # Generate angles from 0 to 360 (inclusive)
        angles = [i for i in range(0, 361)]

        # Create empty lists for h_loss and v_loss
        h_loss = []
        v_loss = []

        g_max = self.params['max_gain_dbi']  # for attenuation calc.

        # Calculate h_loss and v_loss arrays' values
        for angle in angles:
            # calc. gain, then attenuation, then append
            h_loss.append(round(g_max - self.gain(elevation=0), 2))
            # calc. gain, then attenuation, then append
            v_loss.append(round(g_max - self.gain(elevation=angle), 2))

        # Complete specs dict. with angle/loss data
        self.specs['h_pattern_datapoint']['phi'] = angles
        self.specs['h_pattern_datapoint']['loss'] = h_loss

        self.specs['v_pattern_datapoint']['theta'] = angles
        self.specs['v_pattern_datapoint']['loss'] = v_loss


    def gain(self, **kwargs):
        """Compute antenna gain (dBi) at given azimuth and elevation.

        Keyword Args
        ------------
        elevation (int or float):
            elevation angle (degrees) measured from the horizontal
            plane at the site of the antenna(–90 <= theta <= 90)

        Returns
        -------
        int or float
            Antenna gain (dBi) at given elevation angle

        Notes
        -----
        Refer to [1] for the calculation methods:
        - Recommends 2.1 (peak side-lobe patters),
        - Recommends 2.2 (average side-lobe patterns).
        """
        required_keys = {
            "elevation": (int, float),  # Accept int or float for elevation
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
        elevation = kwargs['elevation']

        # Bring angles to expected ranges
        theta_h = self.__normalize_elevation(elevation)

        # Find equivalent angles for tilted antenna
        theta = self.__normalize_tilted_angles(theta_h)

        # select appropriate method for final return
        if self.params['pattern_type'] == 'peak':
            return self.__gain_peak(theta)
        else:
            return self.__gain_average(theta)


    @staticmethod
    def __normalize_elevation(angle):
        """Normalize angle to be between -90 and +90.

        Parameters
        ----------
        angle : int or float
            Elevation angle (degrees)

        Returns
        -------
        int or float
            Elevation angle (degrees) between -90 and +90
        """
        while angle > 90 or angle < -90:
            if angle > 90:
                angle = 180 - angle
            elif angle < -90:
                angle = -180 - angle
        return angle


    def __normalize_tilted_angles(self, theta_h):
        """Modify elevation angles of tilted antenna.

        Parameters
        ----------
        theta_h : int or float
            Elevation angle (degree) measured from the horizontal plane
            at the site of antenna

        Returns
        -------
        int or float
            modified theta_h (degrees)

        Notes
        -----
        Modification is done as per [1] Recommends 2.5
        """
        # Return unmodified theta if 0-tilt angle or none-tilt type
        if (self.params['tilt_type'] == 'none'
                or self.params['tilt_angle_deg'] == 0):
            return theta_h

        beta = self.params['tilt_angle_deg']

        # Calculate modified theta
        theta_h_beta = theta_h + beta
        # Calculate modified theta as per [1] formula (1e)
        if theta_h_beta >= 0:
            theta = 90 * theta_h_beta / (90 + beta)
        else:
            theta = 90 * theta_h_beta / (90 - beta)

        return theta


    def __gain_peak(self, theta):
        """Compute antenna gain (dBi) in given elevation angle

        Only for the case of peak side-lobe patterns for not tilted
        antenna in 0.4-70 GHz frequency range.

        Parameters
        ----------
        theta : int or float
            Elevation angle relative to the angle of the maximum gain
            in the vertical plane (degrees)(–90 <= theta <= 90)

        Returns
        -------
        int or float
            Antenna gain (dBi)

        Notes
        -----
        Refer to [1] Recommends 2.1
        """
        g_0 = self.params['max_gain_dbi']
        k = self.params['k']
        theta_3 = self.params['beamwidth_el_deg']

        theta_4 = theta_3 * math.sqrt(1 - 1 / 1.2 * math.log10(k + 1))
        theta_abs = math.fabs(theta)

        if 0 <= theta_abs < theta_4:
            return g_0 - 12 * ((theta / theta_3)**2)
        elif theta_4 <= theta_abs < theta_3:
            return g_0 - 12 + 10 * math.log10(k + 1)
        elif theta_3 <= theta_abs <= 90:
            return g_0 - 12 + 10 * math.log10((theta_abs / theta_3)**-1.5 + k)


    def __gain_average(self, theta):
        """Compute antenna gain (dBi) in given elevation angle

        Only for the case of average side-lobe patterns for not tilted
        antenna in 0.4-70 GHz frequency range.

        Parameters
        ----------
        theta : int or float
            Elevation angle relative to the angle of the maximum gain
            in the vertical plane (degrees)(–90 <= theta <= 90)

        Returns
        -------
        int or float
            Antenna gain (dBi)

        Notes
        -----
        Refer to [1] Recommends 2.2
        """
        g_0 = self.params['max_gain_dbi']
        k = self.params['k']
        theta_3 = self.params['beamwidth_el_deg']

        theta_5 = theta_3 * math.sqrt(1.25 + 1 / 1.2 * math.log10(k + 1))
        theta_abs = math.fabs(theta)

        if 0 <= theta_abs < theta_3:
            return g_0 - 12 * ((theta / theta_3)**2)
        elif theta_3 <= theta_abs < theta_5:
            return g_0 - 15 + 10 * math.log10(k + 1)
        elif theta_5 <= theta_abs <= 90:
            return g_0 - 15 + 10 * math.log10((theta_abs / theta_3)**-1.5 + k)
