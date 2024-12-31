"""
References:
1.  "Rec. ITU-R F.1245-3. Mathematical model of average and related
radiation patterns for point-to-point fixed wireless system antennas
for use in interference assessment in the frequency range
from 1 GHz to 86 GHz"
"""


import math
from antenna.base import BaseAntenna


class ITUF1245(BaseAntenna):
    """ITU-F.1245-3 Antenna Model."""
    def __init__(self):
        super().__init__()

    PARAMS = {
        # Operating frequency (MHz)
        'oper_freq_mhz': {
            'category': 'mandatory',
            'type': (int, float),
            'range': (1000, 86000),
        },

        # Calculation option
        'calc_opt': {
            'category': 'mandatory',
            'type': str,
            'allowed': ['Rec. 2', 'Rec. 3'],
        },

        # Maximum main-lobe antenna gain (dBi)
        'max_gain_dbi': {
            'category': 'optional',
            'type': (int, float),
            'range': (-29.9, 89.9),
        },

        # Antenna diameter (m)
        'diameter_m': {
            'category': 'optional',
            'type': (int, float),
            'range': (0.001, 99.999),
        },
    }


    def _post_set_params(self):
        """Set dependent and not-set optional parameters.

        This method runs after set_params() of the superclass.
        """
        # Check at least one of optional parameters are provided
        if (self.params.get('diameter_m') is None
                and self.params.get('max_gain_dbi') is None
        ):
            raise ValueError(
                    f"Missing required parameter! At least one of the "
                    f"following parameters must be provided: "
                    f"max_gain_dbi, "
                    f"diameter_m"
            )

        # Find corresponding frequency bands
        frequency = self.params['oper_freq_mhz']
        if frequency < 70000:
            self.params['freq_band'] = '1-70 GHz'
        else:
            self.params['freq_band'] = '70-86 GHz'

        # ~ Calculate all required parameters based on input data ~

        # Ant. diam   Gmax    Case    Note
        # 0           0       Err     message
        # 0           1       1       Ref. to NOTE 2
        # 1           0       2       Ref. to NOTE 2
        # 1           1       3       All params available

        # Input availability case 1
        if (self.params.get('max_gain_dbi') is not None
                and self.params.get('diameter_m') is None):
            self.params['d_to_l'] = self.__d_to_l_from_g_max(self.params['max_gain_dbi'])

        # Input availability case 2
        elif (self.params.get('max_gain_dbi') is None
                and self.params.get('diameter_m') is not None):
            wavelength = self.__wavelength(self.params['oper_freq_mhz'])
            d_to_l = self.params['diameter_m'] / wavelength
            self.params['d_to_l'] = d_to_l
            self.params['max_gain_dbi'] = self.__g_max_from_d_to_l(d_to_l)

        # Input availability case 2
        elif (self.params.get('max_gain_dbi') is not None
              and self.params.get('diameter_m') is not None):
            wavelength = self.__wavelength(self.params['oper_freq_mhz'])
            d_to_l = self.params['diameter_m'] / wavelength
            self.params['d_to_l'] = d_to_l


    def _update_specs(self):
        """Update specs data."""
        # Indicate all parameters used in the modeling in comment
        comment_str = (
                f'Ant. diam to wavelength ratio: {self.params['d_to_l']:,.2f}'
        )

        self.specs["name"] = 'ITU-R F.1245-3'
        self.specs['make'] = 'ITU'
        self.specs['frequency'] = self.params['oper_freq_mhz']
        # Calculate 3 dB beamwidth in azimuth and elevation planes
        phi_3 = 35 / self.params['d_to_l']  # Ref. to [1] Recommends 4
        self.specs['h_width'] = round(phi_3, 2)
        self.specs['v_width'] = round(phi_3, 2)  # same as for h_width
        # Calculate front-to-back ratio
        f_to_b = self.gain(off_axis_angle=0) - self.gain(off_axis_angle=180)
        self.specs['front_to_back'] = round(f_to_b, 2)
        self.specs['gain']  = round(self.params['max_gain_dbi'], 2)
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
        Refer to [1]
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
        phi = kwargs['off_axis_angle']

        # Bring the angle to expected ranges
        phi = self.__normalize_off_axis_angle(phi)

        # route to appropriate private method for final calc
        if self.params['calc_opt'] == 'Rec. 2':
            return self.__gain_rec2(phi)
        else:
            return self.__gain_rec3(phi)


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

    @staticmethod
    def __wavelength(frequency):
        """Compute wavelength.
        Parameters
        ----------
        frequency : int or float
            Frequency (MHz)

        Returns
        -------
        int or float
            Wavelength (m)
        """
        return 299.792458 / frequency


    @staticmethod
    def __d_to_l_from_g_max(g_max):
        """Compute D/l ratio from max antenna gain.

        Parameters
        ----------
        g_max : int or float
            Max. antenna gain (dBi)

        Returns
        -------
        int or float
            Ratio of antenna diameter / wavelength (in the same unit)

        References
        ----------
        Ref. to [1] NOTE 2 of Recommends 4
        """
        return math.pow(10, (g_max - 7.7) / 20)


    @staticmethod
    def __g_max_from_d_to_l(d_to_l):
        """Compute max antenna gain from D/l ratio.

        Parameters
        ----------
        d_to_l : int or float
            Ratio of antenna diameter / wavelength (in the same unit)

        Returns
        -------
        int or float
            Max. antenna gain (dBi)

        References
        ----------
        Ref. to [1] NOTE 2 of Recommends 4
        """
        return 20 * math.log10(d_to_l) + 7.7


    def __gain_rec2(self, phi):
        """Compute antenna gain (dBi) as per [1] Recommends 2.

        Parameters
        ----------
        phi : int or float
            off-axis angle (degrees) [0, +180]

        Returns
        -------
        int or float
            Antenna gain (dBi) at the off-axis angle
        """
        g_max = self.params['max_gain_dbi']

        if phi == 0:
            return g_max  # no more computation

        d_to_l = self.params['d_to_l']
        freq = self.params['freq_band']

        g_1 = 2 + 15 * math.log10(d_to_l)
        phi_m = 20 * (1 / d_to_l) * math.sqrt(g_max - g_1)
        phi_r = 12.02 * (d_to_l**(-0.6))

        if (d_to_l > 100) and (freq == '1-70 GHz'):
            if 0 < phi < phi_m:
                return g_max - 2.5 * 10**-3 * (d_to_l * phi)**2
            elif phi_m <= phi < (max(phi_m, phi_r)):
                return g_1
            elif (max(phi_m, phi_r)) <= phi < 48:
                return 29 - 25 * math.log10(phi)
            elif 48 <= phi <= 180:
                return -13
        elif (d_to_l > 100) and (freq == '70-86 GHz'):
            if 0 < phi < phi_m:
                return g_max - 2.5 * 10**-3 * (d_to_l * phi)**2
            elif phi_m <= phi < (max(phi_m, phi_r)):
                return g_1
            elif (max(phi_m, phi_r)) <= phi < 120:
                return 29 - 25 * math.log10(phi)
            elif 120 <= phi <= 180:
                return -23
        elif (d_to_l <= 100) and (freq == '1-70 GHz'):
            if 0 < phi < phi_m:
                return g_max - 2.5 * 10**-3 * (d_to_l * phi)**2
            elif phi_m <= phi < 48:
                return 39 - 5 * math.log10(d_to_l) - 25 * math.log10(phi)
            elif 48 <= phi <= 180:
                return -3 - 5 * math.log10(d_to_l)
        elif (d_to_l <= 100) and (freq == '70-86 GHz'):
            if 0 < phi < phi_m:
                return g_max - 2.5 * 10**-3 * (d_to_l * phi)**2
            elif phi_m <= phi < 120:
                return 39 - 5 * math.log10(d_to_l) - 25 * math.log10(phi)
            elif 120 <= phi <= 180:
                return -13 - 5 * math.log10(d_to_l)

    def __gain_rec3(self, phi):
        """Compute antenna gain (dBi) as per [1] Recommends 3.

        Parameters
        ----------
        phi : int or float
            off-axis angle (degrees) [0, +180]

        Returns
        -------
        int or float
            Antenna gain (dBi) at the off-axis angle
        """
        g_max = self.params['max_gain_dbi']

        if phi == 0:
            return g_max  # no more computation

        d_to_l = self.params['d_to_l']
        freq = self.params['freq_band']

        if d_to_l > 100:
            g_a = g_max - 2.5 * 10**(-3) * (d_to_l * phi)**2
            g_1 = 2 + 15 * math.log10(d_to_l)
            phi_r = 15.85 * d_to_l**(-0.6)
            # It's not clear how arguments of sin function must be calc.
            # sin_arg = (3 * math.pi * math.radians(phi)
            #           / (2 * math.radians(phi_r)))
            sin_arg = math.radians(
                3 * math.pi * phi
                / (2 * phi_r)
            )
            f_phi = 10 * math.log10(0.9 * math.sin(sin_arg)**2 + 0.1)
            g_b = g_1 + f_phi

            if freq == '1-70 GHz':
                if 0 <= phi < phi_r:
                    return max(g_a, g_b)

                elif phi_r <= phi < 48:
                    return 32 - 25 * math.log10(phi) + f_phi

                elif 48 <= phi <= 180:
                    return -10 + f_phi
            else:
                if 0 <= phi < phi_r:
                    return max(g_a, g_b)

                elif phi_r <= phi < 120:
                    return 32 - 25 * math.log10(phi) + f_phi

                elif 120 <= phi <= 180:
                    return -20 + f_phi
        else:
            g_a = g_max - 2.5 * 10**(-3) * (d_to_l * phi)**2
            g_1 = 2 + 15 * math.log10(d_to_l)
            phi_r = 39.8 * d_to_l**(-0.8)

            # It's not clear how arguments of sin function must be calc.
            # sin_arg = 3 * math.pi * math.radians(phi) \
            #           / (2 * math.radians(phi_r))
            sin_arg = math.radians(
                    3 * math.pi * phi
                    / (2 * phi_r)
            )
            f_phi = 10 * math.log10(0.9 * math.sin(sin_arg)**2 + 0.1)
            g_b = g_1 + f_phi

            if freq == '1-70 GHz':
                if 0 <= phi < phi_r:
                    return max(g_a, g_b)

                elif phi_r <= phi < 48:
                    return 42 - 5 * math.log10(d_to_l) \
                        - 25 * math.log10(phi) + f_phi

                elif 48 <= phi <= 180:
                    return -5 * math.log10(d_to_l) + f_phi
            else:
                if 0 <= phi < phi_r:
                    return max(g_a, g_b)

                elif phi_r <= phi < 120:
                    return 42 - 5 * math.log10(d_to_l) \
                        - 25 * math.log10(phi) + f_phi

                elif 120 <= phi <= 180:
                    return -10 - 5 * math.log10(d_to_l) + f_phi