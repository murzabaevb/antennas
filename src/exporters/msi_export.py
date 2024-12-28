class MSIExport:
    def export(self, data, filename):
        """Export antenna data to a file in MSI Planet format.

        Parameters
        ----------
        data : dict
            Antenna data from the `specs` property.
        filename : str
            Name of the output file.

        References
        ----------
        [1] Radio Mobile - RF propagation simulation software - MSI
            [Online]. Available: http://radiomobile.pe1mew.nl/?The_program___Definitions___MSI&search=msi
        [2] Antenna Pattern Editor 2.0. User Manual [Online]. Available: www.wireless-planning.com
        """

        # Remove angles above 360 (inclusive) from H-pattern data
        h_data = [
            (phi, loss)
            for phi, loss in zip(data['h_pattern_datapoint']['phi'],
                                 data['h_pattern_datapoint']['loss'])
            if phi < 360  # Keep angles less than 360
        ]
        h_data_sorted = sorted(h_data)  # Sort by angle (phi)

        # Remove angles above 360 (inclusive) from V-pattern data
        v_data = [
            (theta, loss)
            for theta, loss in zip(data['v_pattern_datapoint']['theta'],
                                 data['v_pattern_datapoint']['loss'])
            if theta < 360  # Keep angles less than 360
        ]
        v_data_sorted = sorted(v_data)  # Sort by angle (theta)

        # Write data in MSI format to a file
        with open(filename, 'w') as file:
            # Write basic antenna information
            file.write(f"NAME {data['name']}\n")
            file.write(f"MAKE {data['make']}\n")
            file.write(f"FREQUENCY {data['frequency']} MHz\n")
            file.write(f"H_WIDTH {data['h_width']} Deg.\n")
            file.write(f"V_WIDTH {data['v_width']} Deg.\n")
            file.write(f"FRONT_TO_BACK {data['front_to_back']} dB\n")
            file.write(f"GAIN {data['gain']} dBi\n")
            file.write(f"TILT {data['tilt']} Deg.\n")
            file.write(f"POLARIZATION {data['polarization']}\n")
            file.write(f"COMMENT {data['comment']}\n")
            file.write(f"HORIZONTAL 360\n")
            for phi, loss in h_data_sorted:
                file.write(f"{phi} {loss}\n")
            file.write(f"VERTICAL 360\n")
            for theta, loss in v_data_sorted:
                file.write(f"{theta} {loss}\n")