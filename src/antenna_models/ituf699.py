"""
References:
1.  "Rec. ITU-R F.699-8. Reference radiation patterns for fixed wireless
system antennas for use in coordination studies and interference
assessment in the frequency range from 100 MHz to 86 GHz"
"""


import math
from base import BaseAntenna


class ITUF699(BaseAntenna):
    """ITU-F.699-8 Antenna Model."""
    def __init__(self):
        super().__init__()

    PARAMS = {
        # Operating frequency (MHz)
        'oper_freq_mhz': {
            'category': 'mandatory',
            'type': (int, float),
            'range': (100, 86000),
        },

        # Antenna diameter (m)
        'diameter_m': {
            'category': 'optional',
            'type': (int, float),
            'range': (0.001, 99.999),
        },

        # Maximum main-lobe antenna gain (dBi)
        'max_gain_dbi': {
            'category': 'optional',
            'type': (int, float),
            'range': (-29.9, 89.9),
        },

        # 3dB beamwidth (degrees)
        'beamwidth_deg': {
            'category': 'optional',
            'type': (int, float),
            'range': (0.001, 179.999),
        },
    }


    def _post_set_params(self):
        """Set dependent and not-set optional parameters.

        This method runs after set_params() of the superclass.
        """
        # Check at least one of optional parameters are provided
        if (self.params.get('diameter_m') is None
                and self.params.get('max_gain_dbi') is None
                and self.params.get('beamwidth_deg') is None
        ):
            raise ValueError(
                    f"Missing required parameter! At least one of the "
                    f"following parameters must be provided: "
                    f"max_gain_dbi, "
                    f"diameter_m, "
                    f"beamwidth_deg"
            )

        # Find corresponding frequency bands
        frequency = self.params['oper_freq_mhz']
        if frequency <= 1000:
            self.params['freq_band'] = '0.1-1 GHz'
        elif 1000 < frequency <= 70000:
            self.params['freq_band'] = '1-70 GHz'
        elif 70000 < frequency <= 86000:
            self.params['freq_band'] = '70-86 GHz'

        # ~ Calculate all required parameters based on input data ~

        # Beamwidth Ant. diam   Gmax    Case    Note
        # 0         0           0       Err     message
        # 0         0           1       1       Ref. Recommends 3
        # 0         1           0       2       Ref. Recommends 3
        # 0         1           1       3       All params available
        # 1         0           0       4       Ref. Recommends 4
        # 1         0           1       5       same as case 1
        # 1         1           0       6       same as case 2
        # 1         1           1       7       same as case 3

        # Input availability case 1
        if (self.params.get('max_gain_dbi') is not None
                and self.params.get('diameter_m') is None
                and self.params.get('beamwidth_deg') is None):
            self.params['d_to_l'] = self.__d_to_l_from_g_max(self.params['max_gain_dbi'])
        # Input availability case 2
        elif (self.params.get('max_gain_dbi') is None
                and self.params.get('diameter_m') is not None
                and self.params.get('beamwidth_deg') is None):
            wavelength = self.__wavelength(self.params['oper_freq_mhz'])
            d_to_l = self.params['diameter_m'] / wavelength
            self.params['d_to_l'] = d_to_l
            self.params['max_gain_dbi'] = self.__g_max_from_d_to_l(d_to_l)
        # Input availability case 3
        elif (self.params.get('max_gain_dbi') is not None
              and self.params.get('diameter_m') is not None
              and self.params.get('beamwidth_deg') is None):
            wavelength = self.__wavelength(self.params['oper_freq_mhz'])
            d_to_l = self.params['diameter_m'] / wavelength
            self.params['d_to_l'] = d_to_l
        # Input availability case 4
        elif (self.params.get('max_gain_dbi') is None
              and self.params.get('diameter_m') is None
              and self.params.get('beamwidth_deg') is not None):
            self.params['d_to_l'] = self.__d_to_l_from_beamwidth(self.params['beamwidth_deg'])
            self.params['max_gain_dbi'] = self.__g_max_from_beamwidht(self.params['beamwidth_deg'])
        # Input availability case 5
        elif (self.params.get('max_gain_dbi') is not None
              and self.params.get('diameter_m') is None
              and self.params.get('beamwidth_deg') is not None):
            # This case is same as case 1 above
            self.params['d_to_l'] = self.__d_to_l_from_g_max(self.params['max_gain_dbi'])
        # Input availability case 6
        elif (self.params.get('max_gain_dbi') is None
              and self.params.get('diameter_m') is not None
              and self.params.get('beamwidth_deg') is not None):
            # It is the same as the case 2 above
            wavelength = self.__wavelength(self.params['oper_freq_mhz'])
            d_to_l = self.params['diameter_m'] / wavelength
            self.params['d_to_l'] = d_to_l
            self.params['max_gain_dbi'] = self.__g_max_from_d_to_l(d_to_l)
        # Input availability case 7
        elif (self.params.get('max_gain_dbi') is not None
              and self.params.get('diameter_m') is not None
              and self.params.get('beamwidth_deg') is not None):
            # It is the same as the case 3 above
            wavelength = self.__wavelength(self.params['oper_freq_mhz'])
            d_to_l = self.params['diameter_m'] / wavelength
            self.params['d_to_l'] = d_to_l


    def _update_specs(self):
        """Update specs data."""
        # Indicate all parameters used in the modeling in comment
        comment_str = (
                f"Ant. diam to wavelength ratio: {self.params['d_to_l']:,.2f}"
        )

        self.specs['name'] = 'ITU-R F.699-8'
        self.specs['make'] = 'ITU'
        self.specs['frequency'] = self.params['oper_freq_mhz']
        # Calculate 3 dB beamwidth in azimuth and elevation planes
        phi_3 = self.__beamwidth_from_g_max(self.params['max_gain_dbi'])
        self.specs['h_width'] = round(phi_3, 2)
        self.specs['v_width'] = round(phi_3, 2)  # same as for h_width
        self.specs['front_to_back'] = 'n/a'
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
        # depending on the antenna Diameter / wavelength ratio
        if self.params['freq_band'] == '0.1-1 GHz':
            if self.params['d_to_l'] < 0.63:
                raise ValueError(f"ITU-R F.699-8 applies only D/l>0.63!")
            else:
                return self.__gain_23(phi)

        elif self.params['d_to_l'] > 100:
            return self.__gain_21(phi)

        elif self.params['d_to_l'] <= 100:
            return self.__gain_22(phi)


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
    def __d_to_l_from_beamwidth(beamwidth):
        """Compute D/l ratio using -3dB beamwidth.

        Parameters
        ----------
        beamwidth : int or float
            -3dB beamwidth (angles)

        Returns
        -------
        int or float
            D/l ratio (unitless)

        References
        ----------
        Ref. to [1] Recommends 4.1
        """
        return 70 / beamwidth

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
        Ref. to [1] Recommends 3
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
        Ref. to [1] Recommends 3
        """
        return 20 * math.log10(d_to_l) + 7.7


    @staticmethod
    def __g_max_from_beamwidht(beamwidth):
        """Compute max antenna gain from -3dB beamwidth.

        Parameters
        ----------
        beamwidth : int or float
            -3dB beamwidth of the antenna (degrees)

        Returns
        -------
        int or float
            Max. antenna gain (dBi)

        References
        ----------
        Ref. to [1] Recommends 4.2
        """
        return 44.5 - 20 * math.log10(beamwidth)

    @staticmethod
    def __beamwidth_from_g_max(g_max):
        """Compute -3dB beamwidth from max antenna gain.

        Parameters
        ----------
        g_max : int or float
            Max antenna gain (dBi)

        Returns
        -------
        int or float
            -3dB beamwidth of the antenna (degrees)

        References
        ----------
        Ref. to [1] Recommends 4.2
        """
        return math.pow(10, (44.5 - g_max) / 20)


    def __gain_21(self, phi):
        """Compute antenna gain as per [1] Recommends 2.1.

        This is the case when Antenna Diameter / wavelength > 100

        Parameters
        ----------
        phi : int or float
            Off-axis angle (degrees) [0, 180]

        Returns
        -------
        int or float
            Antenna gain (dBi) for given off-axis angle
        """

        g_max = self.params['max_gain_dbi']

        if phi == 0:
            return g_max  # no more calculations

        d_to_l = self.params['d_to_l']
        g_1 = 2 + 15 * math.log10(d_to_l)
        phi_m = 20 * 1 / d_to_l * (g_max - g_1) ** 0.5
        if isinstance(phi_m, complex):
            raise ValueError(f"Error! phi_m in Rec. 2.1.2 became complex number!")
        phi_r = 15.85 * d_to_l ** (-0.6)

        if self.params['freq_band'] == '1-70 GHz':
            if 0 < phi < phi_m:
                return g_max - 2.5 * 10 ** (-3) * (d_to_l * phi) ** 2

            elif phi_m <= phi < phi_r:
                return g_1

            elif phi_r <= phi < 48:
                return 32 - 25 * math.log10(phi)

            elif 48 <= phi <= 180:
                return -10

        elif self.params['freq_band'] == '70-86 GHz':
            if 0 < phi < phi_m:
                return g_max - 2.5 * 10**(-3) * (d_to_l * phi)**2

            elif phi_m <= phi < phi_r:
                return g_1

            elif phi_r <= phi < 120:
                return 32 - 25 * math.log10(phi)

            elif 120 <= phi <= 180:
                return -20

    def __gain_22(self, phi):
        """Compute antenna gain as per [1] Recommends 2.2.

        This is the case Antenna Diameter / wavelength <= 100

        Parameters
        ----------
        phi : int or float
            Off-axis angle (degrees) [0, 180]

        Returns
        -------
        int or float
            Antenna gain (dBi) for given off-axis angle
        """
        g_max = self.params['max_gain_dbi']

        if phi == 0:
            return g_max  # no more calculations

        d_to_l = self.params['d_to_l']
        g_1 = 2 + 15 * math.log10(d_to_l)
        phi_m = 20 * 1 / d_to_l * (g_max - g_1)**0.5

        if self.params['freq_band'] == '1-70 GHz':
            if 0 < phi < phi_m:
                return g_max - 2.5 * 10**(-3) * (d_to_l * phi)**2

            elif phi_m <= phi < (100 / d_to_l):
                return g_1

            elif (100 / d_to_l) <= phi < 48:
                return 52 - 10 * math.log10(d_to_l) - 25 * math.log10(phi)

            elif 48 <= phi <= 180:
                return 10 - 10 * math.log10(d_to_l)

        elif self.params['freq_band'] == '70-86 GHz':
            if 0 < phi < phi_m:
                return g_max - 2.5 * 10**(-3) * (d_to_l * phi)**2

            elif phi_m <= phi < (100 / d_to_l):
                return g_1

            elif (100 / d_to_l) <= phi < 120:
                return 52 - 10 * math.log10(d_to_l) - 25 * math.log10(phi)

            elif 120 <= phi <= 180:
                return -10 * math.log10(d_to_l)

    def __gain_23(self, phi):
        """Compute antenna gain as per [1] Recommends 2.3.

        This is the case Antenna Diameter / wavelength > 0.63

        Parameters
        ----------
        phi : int or float
            Off-axis angle (degrees) [0, 180]

        Returns
        -------
        int or float
            Antenna gain (dBi) for given off-axis angle
        """
        g_max = self.params['max_gain_dbi']

        if phi == 0:
            return g_max  # no more calculations

        d_to_l = self.params['d_to_l']
        g_1 = 2 + 15 * math.log10(d_to_l)
        phi_m = 20 * 1 / d_to_l * (g_max - g_1)**0.5
        phi_s = 144.5 * d_to_l**(-0.2)

        if 0 < phi < phi_m:
            return g_max - 2.5 * 10**(-3) * (d_to_l * phi)**2

        elif phi_m <= phi < (100 / d_to_l):
            return g_1

        elif (100 / d_to_l) <= phi < phi_s:
            return 52 - 10 * math.log10(d_to_l) - 25 * math.log10(phi)

        elif phi_s <= phi <= 180:
            return -2 - 5 * math.log10(d_to_l)
