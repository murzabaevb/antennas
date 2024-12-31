"""
References:
1.  "Rec. ITU-R F.1336-5. Reference radiation patterns of
    omnidirectional, sectoral and other antennas for the fixed
    and mobile services for use in sharing studies in the
    frequency range from 400 MHz to about 70 GHz"
"""


import math
from antenna.base import BaseAntenna


class ITUF1336s(BaseAntenna):
    """ITU-F.1336-5 Sectoral Antenna Model."""
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

        # 3dB beamwidth (degrees) in the azimuth plane
        'beamwidth_az_deg': {
            'category': 'mandatory',
            'type': (int, float),
            'range': (0.1, 359.9),
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
            'allowed': ['none', 'mechanical', 'electrical'],
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
            'category': 'conditional',
            'type': (int, float),
            'range': (0.1, 179.9),
            'depends_on': {'beamwidth_az_deg': lambda x: x > 120},
        },

        # Parameter accomplishing the relative minimum gain for
        # peak side-lobe patterns (typical value 0.7).
        'k_p': {
            'category': 'optional',
            'type': float,
            'range': (0.001, 0.999),
        },

        # Parameter accomplishing the relative minimum gain for
        # average side-lobe patterns (typical value 0.7)
        'k_a': {
            'category': 'optional',
            'type': float,
            'range': (0.001, 0.999),
        },

        # Azimuth pattern adjustment factor based on leaked power.
        # typ. antenna 0.8; improved side-lobe performance antenna 0.7.
        'k_h': {
            'category': 'optional',
            'type': float,
            'range': (0.001, 0.999),
        },

        # Elevation pattern adjustment factor based on leaked power.
        # typ. antenna 0.7; improved side-lobe performance antenna 0.3.
        'k_v': {
            'category': 'optional',
            'type': float,
            'range': (0.001, 0.999),
        },
    }


    def _post_set_params(self):
        """Set dependent and not set optional parameters.

        This method runs after set_params() of the superclass.
        """
        # Set the frequency range
        if self.params['oper_freq_mhz'] <= 6000:
            self.params['freq_range'] = '0.4-6 GHz'
        else:
            self.params['freq_range'] = '6-70 GHz'

        # Set downward tilt angle (degrees) if not set
        if (self.params.get('tilt_angle_deg') is None
                or self.params['tilt_type'] == 'none'):
            self.params['tilt_angle_deg'] = 0

        # Set 3dB beamwidth (degrees) if not set
        if self.params.get('beamwidth_el_deg') is None:
            self.params['beamwidth_el_deg'] = self.__theta_3()

        # Set k_p factor if not set
        if self.params.get('k_p') is None:
            self.params['k_p'] = 0.7 # default value

        # Set k_a factor if not set
        if self.params.get('k_a') is None:
            self.params['k_a'] = 0.7  # default value

        # Set k_h factor if not set
        if self.params.get('k_h') is None:
            if self.params['performance_type'] == 'typical':
                self.params['k_h'] = 0.8 # default for typical
            else:
                self.params['k_h'] = 0.7  # default for improved

        # Set k_v factor if not set
        if self.params.get('k_v') is None:
            if self.params['performance_type'] == 'typical':
                self.params['k_v'] = 0.7 # default for typical
            else:
                self.params['k_v'] = 0.3  # default for improved


    def _update_specs(self):
        """Update specs data."""
        # Indicate all parameters used in the modeling in comment
        comment_str = (
                f'Side-lobe: '
                f'{self.params['pattern_type']}/'
                f'{self.params['performance_type']}, '
                f'tilting: {self.params['tilt_type']}, '
                f'kp={self.params['k_p']}, '
                f'ka={self.params['k_a']}, '
                f'kh={self.params['k_h']}, '
                f'kv={self.params['k_v']}'
        )

        self.specs["name"] = 'ITU-R F.1336-5 Sectoral'
        self.specs['make'] = 'ITU'
        self.specs['frequency'] = self.params['freq_range']
        self.specs['h_width'] = self.params['beamwidth_az_deg']
        self.specs['v_width'] = round(self.params['beamwidth_el_deg'], 2)
        self.specs['front_to_back'] = 'n/a'
        self.specs['gain']  = self.params['max_gain_dbi']
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
            h_loss.append(round(g_max - self.gain(azimuth=angle, elevation=0), 2))
            # need the azimuth to point back when elevation points back
            if 90 < angle < 270:
                phi = 180
            else:
                phi = 0
            # calc. gain, then attenuation, then append
            v_loss.append(round(g_max - self.gain(azimuth=phi, elevation=angle), 2))

        # Complete specs dict. with angle/loss data
        self.specs['h_pattern_datapoint']['phi'] = angles
        self.specs['h_pattern_datapoint']['loss'] = h_loss

        self.specs['v_pattern_datapoint']['theta'] = angles
        self.specs['v_pattern_datapoint']['loss'] = v_loss


    def __theta_3(self):
        """Compute 3dB beamwidth (degrees) in elevation plane.

        Returns:
        float: 3dB beamwidth (degrees) in elevation plane.

        Notes:
        See Ref. [1] Recommends 3.3
        """
        g_0 = self.params['max_gain_dbi']
        phi_3 = self.params['beamwidth_az_deg']

        return (31000.0 * 10 ** (-0.1 * g_0)) / phi_3


    def gain(self, **kwargs):
        """Compute antenna gain (dBi) at given azimuth and elevation.

        Keyword Args
        ------------
        azimuth (int or float) :
            Azimuth angle (degrees) in the horizontal plane at the
            site of the antenna measured from the azimuth of maximum gain
        elevation (int or float) :
            Elevation angle (degree) measured from the horizontal plane
            at the site of antenna

        Returns
        -------
        int or float
            Antenna gain (dBi) at given azimuth and elevation

        Notes
        -----
        Refer to [1] for the calculation methods:
        - Recommends 3.1.1 (peak side-lobe patters in 0.4-6 GHz),
        - Recommends 3.1.2 (average side-lobe patterns in 0.4-6 GHz),
        - Recommends 3.2.1 (peak side-lobe patters in 6-70 GHz),
        - Recommends 3.2.2 (average side-lobe patterns in 6-70 GHz)
        - Recommends 3.4, 3.5 (for tilted antennas)
        """

        # Define expected keys and their types
        required_keys = {
            "azimuth": (int, float),  # Accept int or float for azimuth
            "elevation": (int, float)  # Accept int or float for elevation
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
        azimuth = kwargs['azimuth']
        elevation = kwargs['elevation']

        # Bring angles to expected ranges
        phi_h = self.__normalize_azimuth(azimuth)
        theta_h = self.__normalize_elevation(elevation)

        # Find equivalent angles for tilted antenna
        angles = self.__normalize_tilted_angles(phi_h, theta_h)
        phi = angles['phi']
        theta = angles['theta']

        if self.params['freq_range'] == '0.4-6 GHz':
            # re-direction based on pattern type
            if self.params['pattern_type'] == 'average':
                return self.__gain_average_04_6ghz(phi, theta)
            else:  # follow 'peak' root
                return self.__gain_peak_04_6ghz(phi, theta)
        else:  # follow '6-70 GHz' root
            # re-direction based on pattern type
            if self.params['pattern_type'] == 'average':
                return self.__gain_average_6_70ghz(phi, theta)
            else:  # follow 'peak' root
                return self.__gain_peak_6_70ghz(phi, theta)


    @staticmethod
    def __normalize_azimuth(angle):
        """Normalize angle to be between -180 and +180 degrees.

        Parameters
        ----------
        angle : int or float
            Azimuth angle (degrees)

        Returns
        -------
        int or float
            Azimuth angle (degrees) between -180 and +180
        """
        angle = angle % 360
        if angle > 180:
            angle -= 360
        return angle


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


    def __normalize_tilted_angles(self, phi_h, theta_h):
        """Modify azimuth and elevation angles of tilted antenna.

        Parameters
        ----------
        phi_h : int of float
            Azimuth angle (degrees) in the horizontal plane at the
            site of the antenna measured from the azimuth of maximum gain
        theta_h : int or float
            Elevation angle (degree) measured from the horizontal plane
            at the site of antenna

        Returns
        -------
        dict
            A dictionary with the following key-value pairs:
            - 'phi' (int or float): modified phi_h (degrees)
            - 'theta' (int or float): modified theta_h (degrees)

        Notes
        -----
        Modification is done as per [1] Recommends 3.4 and 3.5
        """
        # Return unmodified phi/theta if 0-tilt angle & none-tilt type
        if (self.params['tilt_type'] == 'none'
                and self.params['tilt_angle_deg'] == 0):
            return {'phi': phi_h, 'theta': theta_h}

        # Variables to be returned at the end
        phi = None
        theta = None

        # Convert angles to radians
        phi_h_rad = math.radians(phi_h)
        theta_h_rad = math.radians(theta_h)
        beta = self.params['tilt_angle_deg']
        beta_rad = math.radians(beta)

        # Cos and Sin of angles
        sin_theta_h = math.sin(theta_h_rad)
        cos_beta = math.cos(beta_rad)
        cos_theta_h = math.cos(theta_h_rad)
        cos_phi_h = math.cos(phi_h_rad)
        sin_beta = math.sin(beta_rad)

        # Calculate modified theta and phi for mechanical tilt case
        # Refer to [1] formula (3b)
        asin_arg = sin_theta_h * cos_beta + cos_theta_h * cos_phi_h * sin_beta
        asin_arg = max(-1.0, min(1.0, asin_arg))  # clamp by [-1, 1]
        theta = math.degrees(math.asin(asin_arg))
        # Refer to [1] formula (3c)
        theta_rad = math.radians(theta)
        cos_theta = math.cos(theta_rad)
        # acos_arg = ((cos_theta_h * cos_phi_h * cos_beta
        #             - sin_theta_h * sin_beta)
        #             / cos_theta)
        acos_arg = (
                (
                        -sin_theta_h * sin_beta
                        + cos_theta_h * cos_phi_h * cos_beta
                )
                / cos_theta
        )
        acos_arg = max(-1.0, min(1.0, acos_arg))  # clamp by [-1, 1]
        phi = math.degrees(math.acos(acos_arg))

        # Re-calculate theta in case of electrical tilt
        if self.params['tilt_type'] == 'electrical':
            theta_h_beta = theta_h + beta
            # Calculate modified theta as per [1] formula (1e)
            if theta_h_beta >= 0:
                theta = 90 * theta_h_beta / (90 + beta)
            else:
                theta = 90 * theta_h_beta / (90 - beta)

        return {'phi': phi, 'theta': theta}


    def __gain_peak_04_6ghz(self, phi, theta):
        """Compute antenna gain (dBi) in given direction.

        Only for the case of peak side-lobe patterns for not tilted
        antenna in 0.4-6 GHz frequency range.

        Parameters
        ----------
        phi : int or float
            Azimuth angle relative to the angle of the maximum gain
            in the horizontal plane (degrees) (–180 <= phi <= 180)
        theta : int or float
            Elevation angle relative to the angle of the maximum gain
            in the vertical plane (degrees)(–90 <= theta <= 90)

        Returns
        -------
        int or float
            Antenna gain (dBi)

        Notes
        -----
        Refer to [1] Recommends 3.1.1
        """

        phi_3 = self.params['beamwidth_az_deg']
        theta_3 = self.params['beamwidth_el_deg']
        g_0 = self.params['max_gain_dbi']

        x_h = math.fabs(phi) / phi_3  # Ref. [1] Recommends 3.1.1
        x_v = math.fabs(theta) / theta_3  # Ref. [1] Recommends 3.1.1

        # Calculate horizontal gain compression ratio
        # Ref. [1] Recommends 3.1.1, formula (2a2)
        r = ((self.__g_hr_peak(x_h) - self.__g_hr_peak(180 / phi_3))
             / (self.__g_hr_peak(0) - self.__g_hr_peak(180 / phi_3)))

        # Calculate resulting gain Ref. [1] Recommends 3.1.1
        return (g_0 + self.__g_hr_peak(x_h)
                + r * self.__g_vr_peak(x_v))


    def __g_hr_peak(self, x_h):
        """Compute relative reference antenna gain in azimuth plane.

        Parameters
        ----------
        x_h : float
            Ratio of abs(phi) / phi_3

        Returns
        -------
        int or float
            Relative reference antenna gain in the azimuth plane

        Notes
        -----
        Refer to [1] Recommends 3.1.1.2
        """
        k_h = self.params['k_h']
        lambda_kh = 3 * (1 - 0.5**-k_h)
        g_180 = self.__g_180_peak()

        # Ref. to [1] Recommends 3.1.1.1.2, formula (2b2)
        if x_h <= 0.5:
            return_val = -12 * x_h**2
        else:
            return_val = -12 * x_h**(2 - k_h) - lambda_kh

        if return_val >= g_180:
            return return_val
        else:
            return g_180


    def __g_180_peak(self):
        """Compute relative minimum gain (dB)

        Returns
        -------
        int or float
            Relative minimum gain (dBi)

        Notes
        -----
        Refer to [1] Recommends 3.1.1.1
        """
        k_p = self.params['k_p']
        theta_3 = self.params['beamwidth_el_deg']

        return (-12 + 10 * math.log10(1 + 8 * k_p)
                - 15 * math.log10(180 / theta_3))


    def __g_vr_peak(self, x_v):
        """Compute relative reference antenna gain in elevation plane.

        Parameters
        ----------
        x_v : float
            The ratio of abs(theta)/theta_3

        Returns
        -------
        int or float
            Relative reference antenna gain in elevation plane

        Notes
        -----
        Refer [1] to Recommends 3.1.1.3
        """

        k_v = self.params['k_v']
        theta_3 = self.params['beamwidth_el_deg']

        x_k = math.sqrt(1 - 0.36 * k_v)
        g_180 = self.__g_180_peak()
        c = self.__c_peak()
        lambda_kv = (12 - c * math.log10(4)
                     - 10 * math.log10(4**-1.5 + k_v))

        # Ref. to [1] Recommends 3.1.1.3, Formula (2b3)
        if x_v < x_k:
            return -12 * x_v**2
        elif (x_k <= x_v) and (x_v < 4):
            return -12 + 10 * math.log10(x_v**-1.5 + k_v)
        elif (4 <= x_v) and (x_v < (90 / theta_3)):
            return -lambda_kv - c * math.log10(x_v)
        elif x_v >= (90 / theta_3):
            return g_180


    def __c_peak(self):
        """Compute attenuation incline factor (C).

        Returns
        -------
        int or float
            Attenuation incline factor

        Notes
        -----
        Refer to [1] Recommends 3.1.1.3
        """

        theta_3 = self.params['beamwidth_el_deg']
        k_v = self.params['k_v']
        k_p = self.params['k_p']

        block_1 = math.pow(180 / theta_3, 1.5)
        block_2 = math.pow(4, -1.5) + k_v
        block_3 = math.log10(22.5 / theta_3)

        return math.log10(block_1 * block_2 / (1 + 8 * k_p)) / block_3



    def __gain_average_04_6ghz(self, phi, theta):
        """Compute antenna gain (dBi) in given direction.

        Only for the case of average side-lobe patterns for not tilted
        antenna in 0.4-6 GHz frequency range.

        Parameters:
        phi : int or float
            Azimuth angle (degrees) relative to the angle of the
            maximum gain in the horizontal plane (–180 <= phi <= 180)
        theta : int or float
            Elevation angle (degrees) relative to the angle of the
            maximum gain in the vertical plane (–90 <= theta <= 90)

        Returns
        -------
        int or float
            Antenna gain (dBi)

        Notes
        -----
        Refer to [1] Recommends 3.1.2 for the calculation method
        """
        phi_3 = self.params['beamwidth_az_deg']
        theta_3 = self.params['beamwidth_el_deg']
        g_0 = self.params['max_gain_dbi']

        x_h = math.fabs(phi) / phi_3  # Ref. [1] Recommends 3.1.1
        x_v = math.fabs(theta) / theta_3  # Ref. [1] Recommends 3.1.1

        # Calculate horizontal gain compression ratio
        # Ref. [1] Recommends 3.1.1, formula (2a2)
        r = ((self.__g_hr_average(x_h) - self.__g_hr_average(180 / phi_3))
             / (self.__g_hr_average(0) - self.__g_hr_average(180 / phi_3)))

        # Calculate resulting gain Ref. [1] Recommends 3.1.2
        return (g_0 + self.__g_hr_average(x_h)
                + r * self.__g_vr_average(x_v))


    def __g_hr_average(self, x_h):
        """Compute relative reference antenna gain in azimuth plane.

        Parameters
        ----------
        x_h : float
            Ratio of abs(phi) / phi_3

        Returns
        -------
        int or float
            Relative reference antenna gain in the azimuth plane

        Notes
        -----
        Refer to [1] Recommends 3.1.2.2
        """
        k_h = self.params['k_h']
        lambda_kh = 3 * (1 - 0.5**-k_h)
        g_180 = self.__g_180_average()

        # Ref. to [1] Recommends 3.1.2.2, formula (2c2)
        if x_h <= 0.5:
            return_val = -12 * x_h**2
        else:
            return_val = -12 * x_h **(2 - k_h) - lambda_kh

        if return_val >= g_180:
            return return_val
        else:
            return g_180


    def __g_180_average(self):
        """Compute relative minimum gain (dB)

        Returns
        -------
        int or float
            Relative minimum gain (dBi)

        Notes
        -----
        Refer to [1] Recommends 3.1.2.1
        """

        k_a = self.params['k_a']
        theta_3 = self.params['beamwidth_el_deg']

        return (-15 + 10 * math.log10(1 + 8 * k_a)
                - 15 * math.log10(180 / theta_3))


    def __g_vr_average(self, x_v):
        """Compute relative reference antenna gain in elevation plane.

        Parameters
        ----------
        x_v : float
            The ratio of abs(theta)/theta_3

        Returns
        -------
        int or float
            Relative reference antenna gain in elevation plane

        Notes
        -----
        Refer to [1] Recommends 3.1.2.3
        """

        k_v = self.params['k_v']
        theta_3 = self.params['beamwidth_el_deg']

        x_k = math.sqrt(1.33 - 0.33 * k_v)
        g_180 = self.__g_180_average()
        c = self.__c_average()
        lambda_kv = (12 - c * math.log10(4)
                     - 10 * math.log10(4 ** -1.5 + k_v))

        # Ref. to [1] Recommends 3.1.2.3, Formula (2c3)
        if x_v < x_k:
            return -12 * x_v ** 2
        elif (x_k <= x_v) and (x_v < 4):
            return -15 + 10 * math.log10(x_v ** -1.5 + k_v)
        elif (4 <= x_v) and (x_v < (90 / theta_3)):
            return -lambda_kv - 3 - c * math.log10(x_v)
        elif x_v >= (90 / theta_3):
            return g_180


    def __c_average(self):
        """Compute attenuation incline factor (C).

        Returns
        -------
        C : int or float
            Attenuation incline factor

        Notes
        -----
        Refer to [1] Recommends 3.1.2.3
        """

        theta_3 = self.params['beamwidth_el_deg']
        k_v = self.params['k_v']
        k_a = self.params['k_a']

        block_1 = math.pow(180 / theta_3, 1.5)
        block_2 = math.pow(4, -1.5) + k_v
        block_3 = math.log10(22.5 / theta_3)

        return math.log10(block_1 * block_2 / (1 + 8 * k_a)) / block_3


    def __gain_peak_6_70ghz(self, phi, theta):
        """Compute antenna gain (dBi) in given direction.

        Only for the case of peak side-lobe patterns for not tilted
        antenna in 6-70 GHz frequency range

        Parameters
        ----------
        phi : int or float
            Azimuth angle relative to the angle of the maximum gain
            in the horizontal plane (degrees) (–180 <= phi <= 180)
        theta : int or float
            Elevation angle relative to the angle of the maximum gain
            in the vertical plane (degrees)(–90 <= theta <= 90)

        Returns
        -------
        int or float
            Antenna gain (dBi)

        Notes
        -----
        Refer to [1] Recommends 3.2.1
        """

        g_0 = self.params['max_gain_dbi']

        psi = self.__psi(phi, theta)  # Ref. to [1] Formula (2d4)
        psi_a = self.__psi_a(phi, theta)  # Ref. to [1] Formula (2d3)

        x = psi / psi_a  # Ref. to [1] Formula (2d5)

        # Final gain calculation Ref. to [1] Formula (2e)
        if (0 <= x) and (x < 1):
            return g_0 - 12 * x**2
        elif 1 <= x:
            return g_0 - 12 - 15 * math.log10(x)


    @staticmethod
    def __psi(phi, theta):
        """Compute psi (degrees).

        Parameters
        ----------
        phi : int or float
            Azimuth angle relative to the angle of the maximum gain
            in the horizontal plane (degrees) (–180 <= phi <= 180)
        theta : int or float
            Elevation angle relative to the angle of the maximum gain
            in the veritical plane (degrees)(–90 <= theta <= 90)

        Returns
        -------
        int or float
            Angle psi (degrees)

        Notes
        -----
        Refer to [1] Recommends 3.2.1
        """
        phi_rad = math.radians(phi)
        theta_rad = math.radians(theta)

        # Ref. to [1] Recommends 3.2.1, formula (2d4)
        acos_arg = math.cos(phi_rad) * math.cos(theta_rad)
        acos_arg = max(-1.0, min(1.0, acos_arg))  # clamping by [-1, 1]
        psi_rad = math.acos(acos_arg)

        return math.degrees(psi_rad)


    def __psi_a(self, phi, theta):
        """Compute psi_a (degrees).

        Parameters
        ----------
        phi : int or float
            Azimuth angle relative to the angle of the maximum gain
            in the horizontal plane (degrees) (–180 <= phi <= 180)
        theta : int or float
            Elevation angle relative to the angle of the maximum gain
            in the vertical plane (degrees)(–90 <= theta <= 90)

        Returns
        -------
        int or float
            Angle psi_a (degrees)

        Notes
        -----
        Refer to [1] Recommends 3.2.1
        """
        phi_3 = self.params['beamwidth_az_deg']
        theta_3 = self.params['beamwidth_el_deg']
        psi = self.__psi(phi, theta)

        if (0 <= psi) and (psi <= 90):
            alpha = self.__alpha(phi, theta)
            alpha_rad = math.radians(alpha)
            a = math.cos(alpha_rad) / phi_3
            b = math.sin(alpha_rad) / theta_3
            return 1 / math.sqrt(a**2 + b**2)
        elif (90 < psi) and (psi <= 180):
            phi_3m = self.__phi_3m(phi, theta)
            theta_rad = math.radians(theta)
            a = math.cos(theta_rad) / phi_3m
            b = math.sin(theta_rad) / theta_3
            return 1 / math.sqrt(a**2 + b**2)


    def __phi_3m(self, phi, theta):
        """Compute equivalent 3 dB beamwidth phi_3m (degrees)
        in the azimuth plane

        Parameters
        ----------
        phi : int or float
            Azimuth angle relative to the angle of the maximum gain
            in the horizontal plane (degrees) (–180 <= phi <= 180)
        theta : int or float
            Elevation angle relative to the angle of the maximum gain
            in the vertical plane (degrees)(–90 <= theta <= 90)

        Returns
        -------
        int or float
            Equivalent 3 dB beamwidth (degrees)

        Notes
        -----
        Refer to [1] Recommends 3.2.1
        """
        phi_3 = self.params['beamwidth_az_deg']
        theta_3 = self.params['beamwidth_el_deg']
        phi_abs = math.fabs(phi)

        # Set phi_th depending on peak or average side-lobe pattern
        if self.params['pattern_type'] == 'peak':
            phi_th = phi_3   # Ref. to [1] Recommends 3.2.1
        else:
            phi_th = 1.152 * phi_3   # Ref. to [1] Recommends 3.2.2

        if (0 <= phi_abs) and (phi_abs <= phi_th):
            return phi_3
        elif (phi_th < phi_abs) and (phi_abs <= 180):
            x = math.radians((phi_abs - phi_th) / (180 - phi_th) * 90)
            a = math.cos(x) / phi_3
            b = math.sin(x) / theta_3
            return 1 / math.sqrt(a**2 + b**2)


    @staticmethod
    def __alpha(phi, theta):
        """Compute alpha (degrees).

        Parameters
        ----------
        phi : int or float
            Azimuth angle relative to the angle of the maximum gain
            in the horizontal plane (degrees) (–180 <= phi <= 180)
        theta : int or float
            Elevation angle relative to the angle of the maximum gain
            in the vertical plane (degrees)(–90 <= theta <= 90)

        Returns
        -------
        float
            Alpha angle (degrees)

        Notes
        -----
        Refer to [1] Recommends 3.2.1
        """
        phi_rad = math.radians(phi)
        theta_rad = math.radians(theta)

        # Ref. to [1] Recommends 3.2.1, formula (2d2)
        # atan2() is used instead atan()
        alpha_rad = math.atan2(
                math.tan(theta_rad),
                math.sin(phi_rad)
        )
        return math.degrees(alpha_rad)


    def __gain_average_6_70ghz(self, phi, theta):
        """Compute antenna gain (dBi) in given direction.

        Only for the case of average side-lobe patterns for not tilted
        antenna in 6-70 GHz frequency range

        Parameters
        ----------
        phi : int or float
            Azimuth angle (degrees) relative to the angle of the
            maximum gain in the horizontal plane (–180 <= phi <= 180)
        theta : int or float
            Elevation angle (degrees) relative to the angle of the
            maximum gain in the vertical plane (–90 <= theta <= 90)

        Returns
        -------
        int or float
            Antenna gain (dBi)

        Notes
        -----
        Refer to [1] Recommends 3.2.2
        """
        g_0 = self.params['max_gain_dbi']

        psi = self.__psi(phi, theta)  # Ref. to [1] Formula (2d4)
        psi_a = self.__psi_a(phi, theta)  # Ref. to [1] Formula (2d3)

        x = psi / psi_a  # Ref. to [1] Formula (2d5)

        # Final gain calculation Ref. to [1] Formula (2f)
        if (0 <= x) and (x < 1.152):
            return g_0 - 12 * x**2
        elif 1.152 <= x:
            return g_0 - 15 - 15 * math.log10(x)