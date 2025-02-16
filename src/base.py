from abc import ABC, abstractmethod
import textwrap
import matplotlib.pyplot as plt
import numpy as np


class BaseAntenna(ABC):
    """Base class for all antenna models."""

    PARAMS = {}  # Child classes will override this

    def __init__(self):
        self.params = {}
        # Refer to MSI Planet file format description
        self.specs = {
            'name': None,  # Name of the antenna
            'make': None,  # Manufacturer's name
            'frequency': None,  # Design frequency of the antenna (MHz)
            'h_width': None,  #  Horizontal beamwidth (deg)
            'v_width': None,  #  Vertical beamwidth (deg)
            'front_to_back': None,  # Front to back ratio (dB)
            'gain': None,  # Antenna gain (dBi)
            'tilt': None,  # Electrical tilt of the main beam (deg)
            'polarization': None,  # Horizontal, Vertical, +/-45 etc.
            'comment': None,  # Any essential information
            'h_pattern_datapoint': {
                'phi': [],  # angle (deg)
                'loss': [],  # attenuation (dB)
            },
            'v_pattern_datapoint': {
                'theta': [],  # angle (deg)
                'loss': [],  # attenuation (dB)
            },
        }


    def set_params(self, **kwargs):
        """Validate and set parameters according to PARAMS."""
        validated_params = {}  # Reset params before setting

        for param, rules in self.PARAMS.items():
            value = kwargs.get(param)

            # Handle Mandatory
            if rules['category'] == 'mandatory' and value is None:
                raise ValueError(f"Missing required parameter '{param}'")

            # Handle Optional
            if rules['category'] == 'optional' and value is None:
                continue  # If not provided, it remains unset

            # Handle Conditional
            if rules['category'] == 'conditional' and 'depends_on' in rules:
                for dep_param, dep_check in rules['depends_on'].items():
                    dep_value = kwargs.get(dep_param)

                    # If dependency is a lambda, evaluate the condition
                    if callable(dep_check):
                        if not dep_check(dep_value):
                            continue  # Dependency not met, so skip validation
                    else:
                        if dep_value != dep_check:
                            continue  # Dependency not met, so skip validation

                    # If we reach this point, the dependency is satisfied, so we need to validate the parameter
                    if value is None:
                        raise ValueError(
                            f"Missing required parameter '{param}' because '{dep_param}' is set to '{dep_value}'")

            # Type Check
            if 'type' in rules and value is not None and not isinstance(value, rules['type']):
                raise TypeError(f"'{param}' must be of type {rules['type']} but got {type(value)}")

            # Range Check
            if 'range' in rules and value is not None and not (rules['range'][0] <= value <= rules['range'][1]):
                raise ValueError(f"'{param}' must be in range {rules['range']} but got {value}")

            # Allowed Values Check
            if 'allowed' in rules and value is not None and value not in rules['allowed']:
                raise ValueError(f"'{param}' must be one of {rules['allowed']} but got '{value}'")

            # Store validated parameter
            validated_params[param] = value

        # Set validated parameters
        self.params = validated_params

        # Call the post-process hook
        self._post_set_params()

    def _post_set_params(self):
        """Hook for subclasses to set dependent parameters."""
        pass


    @abstractmethod
    def gain(self, **kwargs):
        pass


    @abstractmethod
    def _update_specs(self):
        pass


    def show_patterns(self):
        # Update specs property
        self._update_specs()

        # ~ Extract horizontal pattern data from specs property ~

        # Get angles data along converting them to radians
        h_phi = np.radians(self.specs['h_pattern_datapoint']['phi'])
        # Get attenuation/loss data
        h_loss = self.specs['h_pattern_datapoint']['loss']

        # Convert non-numeric values to NaN
        h_loss_cleaned = []
        for loss in h_loss:
            try:
                h_loss_cleaned.append(float(loss))
            except (ValueError, TypeError):
                h_loss_cleaned.append(np.nan)

        # Find the maximum and minimum values, ignoring NaN
        max_h_loss = np.nanmax(h_loss_cleaned)
        min_h_loss = np.nanmin(h_loss_cleaned)

        # Find the max loss value for scaling the radial axis
        h_scale = max_h_loss - min_h_loss

        # ~ Extract vertical pattern data from specs property ~

        # Get angles data along converting them to radians
        v_theta = np.radians(self.specs['v_pattern_datapoint']['theta'])
        # Get attenuation/loss data
        v_loss = self.specs['v_pattern_datapoint']['loss']

        # Convert non-numeric values to NaN
        v_loss_cleaned = []
        for loss in v_loss:
            try:
                v_loss_cleaned.append(float(loss))
            except (ValueError, TypeError):
                v_loss_cleaned.append(np.nan)

        # Find the maximum and minimum values, ignoring NaN
        max_v_loss = np.nanmax(v_loss_cleaned)
        min_v_loss = np.nanmin(v_loss_cleaned)

        # Find the max loss value for scaling the radial axis
        v_scale = max_v_loss - min_v_loss

        # For omni antennas, h_max_loss or v_max_loss could be so small,
        # hence, to make better plot, it is either max of both, or 20 dB
        if h_scale < 3:
            h_scale = 4

        if v_scale < 3:
            v_scale = 4

        # Create a figure with two polar subplots
        fig, (ax1, ax2) = plt.subplots(1, 2,
                   subplot_kw={'projection': 'polar'},
                   figsize=(12, 6)
        )

        # First polar plot (H-pattern):

        ax1.set_theta_offset(np.pi / 2)  # rotate 90 deg. CCW
        ax1.set_theta_direction(-1)  # change direction to CW
        # Plot H-pattern
        ax1.plot(h_phi, h_loss_cleaned, label='H-plane', color='blue', linewidth=3)
        # Title for H-pattern
        ax1.set_title('H-plane', va='bottom', fontsize=12)
        # Set min value at the outer ring; max loss at the center
        # ax1.set_ylim(bottom=max_h_loss, top=min_h_loss)
        ax1.set_ylim(bottom=h_scale, top=min_h_loss)
        # Custom ticks for the radial axis
        ax1.set_yticks(np.linspace(min_h_loss, h_scale, 5))
        # Custom tick labels
        ax1.set_yticklabels([f'{int(val)} dB' for val in
                             np.linspace(min_h_loss, h_scale,
                                         5)])
        # Move the radial labels to 135 degrees to avoid clutter
        ax1.set_rlabel_position(135)


        # Second polar plot (V-pattern):

        # Plot V-pattern
        ax2.plot(v_theta, v_loss_cleaned, label='V-plane', color='blue', linewidth=3)
        # Title for V-pattern
        ax2.set_title('E-plane', va='bottom', fontsize=12)
        # Set min value at the outer ring; max loss at the center
        ax2.set_ylim(bottom=v_scale, top=min_v_loss)
        # Custom ticks for the radial axis
        ax2.set_yticks(np.linspace(min_v_loss, v_scale, 5))
        # Custom tick labels
        ax2.set_yticklabels([f'{int(val)} dB' for val in
                             np.linspace(min_v_loss, v_scale,
                                         5)])
        # Move the radial labels to 135 degrees
        ax2.set_rlabel_position(135)

        # change default plot labels to vary betwen -180, 0, 180
        # 9 equally spaced ticks (0, 45, 90, ..., 360 degrees)
        ax1.set_xticks(np.linspace(0, 2 * np.pi, 9))
        ax2.set_xticks(np.linspace(0, 2 * np.pi, 9))

        # set custom theta tick labels
        ax1.set_xticklabels(
            ['0°', '45°', '90°', '135°', '180°', '-135°', '-90°',
             '-45°', ''])
        ax2.set_xticklabels(
            ['0°', '45°', '90°', '135°', '180°', '-135°', '-90°',
             '-45°', ''])

        # Add antenna settings/parameters to the figure
        info_txt = (
            f"{self.specs['name']}, "
            f"Freq.: {self.specs['frequency']} MHz. "
            f"Beamwidth: {self.specs['h_width']} H / "
            f"{self.specs['v_width']} V deg., "
            f"Gain: {self.specs['gain']} dBi, "
            f"Tilting: {self.specs['tilt']} deg. "
            f"{self.specs['comment']}"
        )

        wrapped_text = "\n".join(textwrap.wrap(info_txt, width=40))
        # set the position for above text info
        fig.text(0.5, 0.95, wrapped_text, wrap=True, ha='center', va='top',
                 fontsize='small', color='gray')

        # Show the plots
        plt.tight_layout()
        plt.show()


    def export(self, exporter, filename):
        """
        Export the antenna's specifications using the given exporter.

        Parameters:
            exporter: An instance of an export class (e.g., CSVExport, JSONExport, YAMLExport).
            filename: The name of the output file.
        """
        # Update specs property
        self._update_specs()

        # Export the data
        exporter.export(self.specs, filename)