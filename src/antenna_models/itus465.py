"""
References:
1.  "Rec. ITU-R S.465-6. Reference radiation pattern for earth station antennas
in the fixed-satellite service for use in coordination and interference
assessment in the frequency range from 2 to 31 GHz"
"""

import math
from base import BaseAntenna


class ITUS465(BaseAntenna):
    """ITU-R S.465-6 Antenna Model."""

    def __init__(self):
        super().__init__()

    PARAMS = {
        # Operating frequency (MHz)
        'oper_freq_mhz': {
            'category': 'optional',
            'type': (int, float),
            'range': (2000, 31000),
        },

        # Antenna diameter (m)
        'diameter_m': {
            'category': 'optional',
            'type': (int, float),
            'range': (0.001, 99.999),
        },

        # Diameter/lambda ratio (unitless)
        'd_to_l': {
            'category': 'optional',
            'type': (int, float),
            'range': (0.001, 10000),
        },
    }

    def _post_set_params(self):
        """Set dependent and not-set optional parameters.

        This method runs after set_params() of the superclass.
        """

        # ~ Calculate all required parameters based on input data ~

        # Freq      Diam        D/l     Case    Action
        # 0         0           0       Err     message
        # 0         0           1       1       all good (take D/l)
        # 0         1           0       2       req. D/l or Freq
        # 0         1           1       3       all good (take D/l)
        # 1         0           0       4       req. D or D/l
        # 1         0           1       5       all good (take D/l)
        # 1         1           0       6       all good (calc. D/l)
        # 1         1           1       7       all good (take D/l)

        # In Case #0
        # superclass won't pass this case

        # In Case #2
        if (self.params.get('oper_freq_mhz') is None
                and self.params.get('diameter_m') is not None
                and self.params.get('d_to_l') is None
        ):
            raise ValueError(
                f"Missing required parameter! At least one of the "
                f"following parameters must also be provided: "
                f"oper_freq_mhz, or "
                f"d_to_l"
            )

        # In Case #4
        if (self.params.get('oper_freq_mhz') is not None
                and self.params.get('diameter_m') is None
                and self.params.get('d_to_l') is None
        ):
            raise ValueError(
                f"Missing required parameter! At least one of the "
                f"following parameters must also be provided: "
                f"diameter_m, or "
                f"d_to_l"
            )

        # in Case #6
        if (self.params.get('oper_freq_mhz') is not None
                and self.params.get('diameter_m') is not None
                and self.params.get('d_to_l') is None
        ):
            wavelength = self.__wavelength(self.params['oper_freq_mhz'])
            d_to_l = self.params['diameter_m'] / wavelength
            self.params['d_to_l'] = d_to_l

        # in all other Cases
        # d_to_l is provided

    def _update_specs(self):
        """Update specs data."""
        # Indicate all parameters used in the modeling in comment

        # For attenuation calculation only
        phi_min = self.__phi_min()
        g_max = round(self.gain(off_axis_angle=phi_min), 2)

        comment_str = (
            f"D/lambda: {self.params['d_to_l']:,.2f}. "
            f"Gain relates to +/-{phi_min:,.2f} deg."
        )

        self.specs['name'] = 'ITU-R S.465-6'
        self.specs['make'] = 'ITU'

        if self.params.get('oper_freq_mhz') is not None:
            freq = round(self.params['oper_freq_mhz'], 6)
        else:
            freq = 'n/a'
        self.specs['frequency'] = freq

        self.specs['h_width'] = 'n/a'
        self.specs['v_width'] = 'n/a'
        self.specs['front_to_back'] = 'n/a'
        self.specs['gain'] = g_max
        self.specs['tilt'] = 0
        self.specs['polarization'] = 'n/a'
        self.specs['comment'] = comment_str

        # Generate angles from 0 to 360 (inclusive)
        angles = [i for i in range(0, 361)]

        # Create empty lists for h_loss
        h_loss = []

        # Calculate h_loss array's values
        for angle in angles:
            gain = self.gain(off_axis_angle=angle)
            if gain is not None:
                h_loss.append(round(g_max - gain, 2))
            else:
                h_loss.append('n/a')

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
            the off-axis angle between the direction of interest and the
            boresight axis (degrees) (0 <= off_axis_angle <= 180)

        Returns
        -------
        None, int or float
            Antenna gain (dBi) at given off-axis angle. If off_axis_angle is
            less than phi_min, None is returned.
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

        phi_min = self.__phi_min()

        # Calculate the gain
        if phi < phi_min:
            d_to_l = self.params['d_to_l']
            return None
        elif phi_min <= phi < 48:
            return 32 - 25 * math.log10(phi)
        else:
            return -10

    def __phi_min(self):
        """Calculate phi_min.

        Returns
        -------
        int or float
            phi_min (degrees) as per [1] Recommends 2 and NOTE 5
        """
        d_to_l = self.params['d_to_l']
        if d_to_l >= 50:
            phi_min = max(1, 100 * (1 / d_to_l))
        elif 33.3 <= d_to_l < 50:
            phi_min = max(2, 114 * d_to_l ** (-1.09))
        else:
            phi_min = 2.5  # Ref. [1] NOTE 5
        return phi_min

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