"""
References:
1.  "Rec. ITU-R S.580-6. Radiation diagrams for use as design objectives
for antennas of earth stations operating with geostationary satellites"
"""

import math

from antenna_models import ITUS465
from base import BaseAntenna


class ITUS580(BaseAntenna):
    """ITU-R S.580-6 Antenna Model."""

    def __init__(self):
        super().__init__()
        # For angles>20 deg. ITU-R S.465 model shall work
        self.s465_antenna = ITUS465()

    PARAMS = {
        # Operating frequency (MHz)
        # Rec. ITU-R S.580-6 doesn't limit; below range is temporary
        'oper_freq_mhz': {
            'category': 'optional',
            'type': (int, float),
            'range': (1000, 100000),
        },

        # Equivalent diameter of antenna (m)
        'diameter_m': {
            'category': 'optional',
            'type': (int, float),
            'range': (0.001, 14.999),  # 15m for D/l=50 & f=1 GHz
        },

        # Diameter/lambda ratio (unitless)
        'd_to_l': {
            'category': 'optional',
            'type': (int, float),
            'range': (50, 10000),  # 50 comes from ITU-R S.580-6
        },
    }


    def __del__(self):
        del self.s465_antenna


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

        # in all other Cases d_to_l is provided

        # Check if resulting d_to_l < 50
        if self.params['d_to_l'] < 50:
            raise ValueError(
                f"Invalid parameter value! d_to_l must be >= 50. "
                f"Resulting value: {self.params['d_to_l']:,.2f}"
            )


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

        self.specs['name'] = 'ITU-R S.580-6'
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
        self.s465_antenna.set_params(d_to_l=self.params['d_to_l'])

        if phi < phi_min:
            return None
        elif phi <= 20:
            return 29 - 25 * math.log10(phi)
        elif phi <= 26.3:
            s465_gain = self.s465_antenna.gain(off_axis_angle=phi)
            return min(-3.5, s465_gain)  # see [1] Note 5
        else:
            return self.s465_antenna.gain(off_axis_angle=phi)


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


    def __phi_min(self):
        """Calculate phi_min.

        Returns
        -------
        int or float
            phi_min (degrees) as per [1] Recommends 1
        """
        d_to_l = self.params['d_to_l']
        return max(1, 100 * 1 / d_to_l)