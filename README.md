## Antenna models

This project provides Python-based antenna models described in various ITU-R Recommendations. Can be used for assessment of co-existence of various terrestrial and space radiocommunication services sharing the radio spectrum. Classes enable to:
- set and/or modify all parameters of antennas considered in the relevant ITU-R recommendations;
- calculate the antenna gains in various azimuth and elevation angles as well as off-the-axis angles;
- display and store the resulting radiation patterns (H- and E-planes);
- export radiation patterns data to CSV, JSON, YAML, MSI for subsequent use in other tools (e.g. MS Excel, Simulation tools).

The project is designed to be modular and extensible, allowing users to implement additional antenna models and customize export formats.

---

### Features

- **modular antenna models**: Includes (so far) implementations for Rec. ITU-F.699, ITU-R F.1245, ITU-F.1336, ITU-R S.465, ITU-R S.580.
- **flexible export options**: Supports exporting radiation patterns to CSV, JSON, YAML, MSI file formats.
- **easy-to-use framework**: Provides a base class for creating and managing antenna models.
- **extensible**: Add other ITU-R and custom models as well as exporters with minimal effort.

---

![Sectoral antenna](https://github.com/murzabaevb/antennas/blob/master/img/TETRA%20BTS%20410-430MHz.png)

---

![Microwave antenna](https://github.com/murzabaevb/antennas/blob/master/img/P2P%20Link%204GHz%20average%20side%20lobes%20v2.png)

---

![Microwave antenna](https://github.com/murzabaevb/antennas/blob/master/img/P2P%20Link%2026GHz%20peak%20side%20lobes.png)

---
### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/murzabaevb/antennas.git
   cd antennas
   ```
   If you wish to work with isolated environment, you may set up and activate a virtual environment:
   ```bash
   python -m venv venv
   # source venv/bin/activate  # On POSIX Platform
   # venv\Scripts\activate.bat  # On Windows: 
   ```
   
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install the package in editable mode:
   ```bash
   pip install -e .
   ```
4. Run `tests/general_test.py` to test the overall functioning and functionalities of the package.
---

### Usage

#### 1. Import the Antenna module

```python
from controller import Antenna
```

#### 2. Create an Object of the Antenna class
```python
your_antenna_name = Antenna('Model_name')
```

Below is the list of arguments one of which has to be passed to the constructor of the Antenna class when creating an Object:

| Model_name  | Rec. ITU-R                                          | Antenna radiation patterns suitable for                                                                           |
|-------------|-----------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|
| `ITUF699`   | [F.699-8](https://www.itu.int/rec/R-REC-F.699/en)   | Fixed wireless system in 0.1-86 GHz range. Models the peak envelope of side-lobe patterns                         |
| `ITUF1245`  | [F.1245-3](https://www.itu.int/rec/R-REC-F.1245/en) | P2P fixed wireless system in 1-86 GHz range. Models the average radiation patterns                                |
| `ITUF1336lg` | [F.1336-5](https://www.itu.int/rec/R-REC-F.1336/en) | Fixed/Mobile services (Low-Gain ant. below 20 dBi) in 1-3 GHz range. Models peak side-lobe patterns.              |
| `ITUF1336o` | [F.1336-5](https://www.itu.int/rec/R-REC-F.1336/en) | Fixed/Mobile services (Omnidirectional ant.) in 0.4-70 GHz range. Models both peak and average side-lobe patterns |
| `ITUF1336s` | [F.1336-5](https://www.itu.int/rec/R-REC-F.1336/en) | Fixed/Mobile services (Sectoral ant.) in 0.4-70 GHz range. Models both peak and average side-lobe patterns        |
| `ITUS465`   | [S.465-6](https://www.itu.int/rec/R-REC-S.465/en)   | FSS ES (peak side-lobe patterns) for coordination/interference assessment in 2-31 GHz range                       |
| `ITUS580`   | [S.580-6](https://www.itu.int/rec/R-REC-S.580/en)   | FSS GSO ES (peak side-lobe patterns) antenna design objectives                                                    |

Below examples show the creation of antenna objects based on needs and requirements.
```python
ant_1 = Antenna('ITUF699')  # P2P microwave antenna (peak radiation patterns)
ant_2 = Antenna('ITUF1245')  # P2P microwave antenna (aver.radiation patterns)
ant_3 = Antenna('ITUF1336lg')  # Low-gain directional antenna
ant_4 = Antenna('ITUF1336o')  # Omnidirectional antenna
ant_5 = Antenna('ITUF1336s')  # Sectoral antenna
ant_6 = Antenna('ITUS465')  # ES antenna 2-31 GHz
ant_7 = Antenna('ITUS580')  # GSO ES antenna
```

#### 3. Set the parameters of the antenna as needed

```python
your_antenna_name.model.set_params(
    # provide
    # keyword 
    # arguments
    # here   
)
```
Depending on the argument passed to the constructor in step 2 above, the following keyword arguments are to be used when setting the parameters of the antenna. If the optional parameters are not provided, either default parameters are used or they are deduced using other provided mandatory parameters based on relevant recommendations/sources:

**For 'ITUS580'**

| Keyword      | Requirement | Value type   | Range             | Description                                                  |
|--------------|-------------|--------------|-------------------|--------------------------------------------------------------|
| `oper_freq_mhz` | optional    | `int, float` | `(1000, 100000)`  | operating frequency (MHz)                                    |
|`diameter_m`| optional    | `int, float` | `(0.001, 14.999)` | antenna diameter (m)                                         |
|`d_to_l`| optional    | `int, float` | `(50, 10000)`     | Antenna diameter to wavelength ratio (both in the same unit) |

*Note: although the frequency, ant. diameter, and D/lambda ratio are indicated as optional, the calculation method is based on D/lambda ratio. Therefore, if D/lambda ratio is not provided, then both frequency and ant. diameter have to be provided together.*

---

**For 'ITUS465'**

| Keyword      | Requirement | Value type   | Range                | Description                                                  |
|--------------|-------------|--------------|----------------------|--------------------------------------------------------------|
| `oper_freq_mhz` | optional    | `int, float` | `(2000, 31000)`      | operating frequency (MHz)                                    |
|`diameter_m`| optional    | `int, float` | `(0.001, 99.999)`    | antenna diameter (m)                                         |
|`d_to_l`| optional    | `int, float` | `(0.001, 10000)`     | Antenna diameter to wavelength ratio (both in the same unit) |

*Note: although the frequency, ant. diameter, and D/lambda ratio are indicated as optional, the calculation method is based on D/lambda ratio. Therefore, if D/lambda ratio is not provided, then both frequency and ant. diameter have to be provided together.*

---

**For 'ITUF699'**

| Keyword      | Requirement | Value type   | Range                | Description                   |
|--------------|-----------|--------------|----------------------|-------------------------------|
| `oper_freq_mhz` | mandatory | `int, float` | `(100, 86000)`       | operating frequency (MHz)|
|`diameter_m`|optional| `int, float` | `(0.001, 99.999)`    | antenna diameter (m)|
|`max_gain_dbi`|optional| `int, float` | `(-29.9, 89.9)`      | max. main-lobe ant. gain (dBi)|
|`beamwidth_deg`|optional| `int, float` | `(0.001, 179.999  )` | 3dB beamwidth (deg.)|

*Note: although ant. diameter, max. gain and beamwidth are indicated as optional, at least one of these must be provided when setting the antenna's parameters.*

---

**For 'ITUF1245'**


| Keyword    | Requirement | Value type   | Range/Option         | Description|
|--|--|--------------|----------------------|--------------------------------|
|`oper_freq_mhz`|mandatory| `int, float` | `(1000, 86000)`      | operating frequency (MHz)|
|`calc_opt`|mandatory| `str`          | `'Rec. 2', 'Rec. 3'` | refer to Note 1 below|
|`max_gain_dbi`|optional|`int, float`| `(-29.9, 89.9 ) `    | max. main-lobe ant. gain (dBi)|
|`diameter_m`|optional|`int, float`| `(0.001, 99.999  ) ` | antenna diameter (m)|

*Note 1: These are the sections of the Rec. ITU-R F.1245 that describing when a particular calculation method is suitable:*
- *Recommends 2: Average radiation patterns of FWS antennas;*
- *Recommends 3: Generalized radiation patterns of point-to-point FWS antennas.*

*Note 2: although ant. diameter and max. gain are indicated as optional, at least one of these must be provided when setting the antenna's parameters.*

---

**For 'ITUF1336lg'**

| Keyword       | Requirement | Value type   | Range         | Description               |
|--|--|--------------|----------------|---------------------------|
|`oper_freq_mhz`|mandatory|`int, float`| `(1000, 3000)` | operating frequency (MHz) |
|`max_gain_dbi`|mandatory|`int, float`| `(-29.9, 20)`  |max. main-lobe ant. gain (dBi)|

---

**For 'ITUF1336o'**

| Keyword           | Requirement | Value type   | Range/Option            | Description|
|--|--|--------------|-------------------------|---------------------------------------|
|`oper_freq_mhz`|mandatory|`int, float`| `(400, 70000)`          | operating frequency (MHz)|
|`max_gain_dbi`|mandatory|`int, float`| `(-29.9, 59.9)`         | max. main-lobe ant. gain (dBi)|
|`pattern_type`|mandatory|`str`| `'average', 'peak'`     | side-lobe pattern type|
|`performance_type`|mandatory|`str`| `'typical', 'improved'` | side-lobe performance type|
|`tilt_type`|mandatory|`str`| `'none', 'electrical'`  | downward tilt type|
|`tilt_angle_deg`|conditional|`int, float`| `(-89.9, 89.9)`         | downward tilt angle (deg.). Required when tilt type is `electrical`|
|`beamwidth_el_deg`|optional|`int, float`| `(0.1, 179.9)`          | 3dB beamwidth (deg.) in elevation plane. Calc. automatically if not provided|
|`k`|optional|`float`| `(0.001, 0.999)`        | parameter accounting increased side-lobe levels. Defaults: k=0.7 for `typical`; k=0 for `improved`|

---

**For 'ITUF1336s'**

| Keyword| Requirement | Value type   | Range/Option| Description|
|--|--|--------------|--------------------------------------|--|
|`oper_freq_mhz`|mandatory| `int, float` | `(400, 70000)`| operating frequency (MHz)|
|`max_gain_dbi`|mandatory| `int, float` | `(-29.9, 59.9)`| max. main-lobe ant. gain (dBi)|
|`beamwidth_az_deg`|mandatory|`int, float`| `(0.1, 359.9) `| 3dB beamwidth (deg.) in azimuth plane|
|`pattern_type`|mandatory|`str`| `'average', 'peak'`| side-lobe pattern type|
|`performance_type`|mandatory|`str`| `'typical', 'improved'`| side-lobe performance type|
|`tilt_type`|mandatory|`str`| `'none', 'mechanical', 'electrical'` | downward tilt type|
|`tilt_angle_deg`|conditional|`int, float`| `(-89.9., 89.9)`| downward tilt angle (deg.). Required when tilt type is not 'none'|
|`beamwidth_el_deg`|conditional|`int, float`| `(0.1, 179.9)`| 3dB beamwidth (deg.) in elevation plane. Required when beamwidth in azimuth plan is above 120 deg.|
|`k_p`|optional|`float`| `(0.001, 0.999)`| parameter accomplishing the relative minimum gain for peak side-lobe patterns. Default: 0.7|
|`k_a`|optional|`float`| `(0.001, 0.999)`| parameter accomplishing the relative minimum gain for average side-lobe patterns. Default: 0.7|
|`k_h`|optional|`float`| `(0.001, 0.999)`| azimuth pattern adjustment factor based on leaked power. Defaults: 0.8 for `typical`, 0.7 for `improved`|
|`k_v`|optional|`float`| `(0.001, 0.999)`| elevation pattern adjustment factor based on leaked power. Defaults: 0.7 for `typical`; 0.3 for `improved`|

Example below demonstrates the settings of IMT BTS antenna in 1-3 GHz range as per [1] [Rep. ITU-R M.2292-0](https://www.itu.int/dms_pub/itu-r/opb/rep/r-rep-m.2292-2014-pdf-e.pdf). 
```python
# Create an object of ITUF1336s Class (sectoral antenna) 
my_antenna = Antenna('ITUF1336s')

# Set antenna parameters as per [1]
my_antenna.model.set_params(
    oper_freq_mhz=806,  # LTE Band 20 DL center frequency
    max_gain_dbi=15,  # [1] Table 2
    beamwidth_az_deg=65, # [1] Table 2
    pattern_type='average',  # [1] is neutral on this
    performance_type='improved',  # Ref. Rec. ITU-R F.1336-5
    tilt_type='electrical',  # [1] is silent on this
    tilt_angle_deg=3,  # [1] Table 2
    # beamwidth_el_deg= ,  # Auto calculated
    # k_p=0.7,  # not required for pattern_type='average'
    k_a=0.7,  # [1] Table 2
    k_h=0.7,  # [1] Table 2
    k_v=0.3,  # [1] Table 2
)
```
Another example is provided below to model the antenna with peak envelope side-lobe patterns of point-to-point fixed systems (aka microwave links) operating in 24.25-29.50 GHz range as per [2] [Rec. ITU-R F.758-7](https://www.itu.int/dms_pubrec/itu-r/rec/f/R-REC-F.758-7-201911-I!!PDF-E.pdf).

```python
# Create an object of ITUF699 Class (microwave link) 
my_antenna = Antenna('ITUF699')

# Set antenna's parameters as per [2]
my_antenna.model.set_params(
    oper_freq_mhz=26875,  # Middle frequency of the range
    max_gain_dbi=48,  # [2] Table 9
)
```
Example of setting the same microwave link's antenna as in above example but with average side-lobe patterns is given below.

```python
# Create an object of ITUF1245 Class (microwave link) 
my_antenna = Antenna('ITUF1245')

# Set antenna's parameters as per [2]
my_antenna.model.set_params(
    oper_freq_mhz=26875,  # Middle frequency of the range
    calc_opt='Rec. 2',  # Average patterns as per Recommends 2
    max_gain_dbi=48,  # [2] Table 9
)
```
#### 4. Further options
Once the parameters of the antenna are set, any of the following functions would be available:
- Calculate the antenna gain in any direction
- Display/store the antenna radiation patterns
- Export the antenna radiation patterns to a file
- Modify antenna parameters

**Calculate the gain of the antenna in required direction**
```python
your_antenna_name.model.gain(
    # provide
    # keyword 
    # arguments
    # here   
)
```
The method returns `int` or `float` number as resulting antenna gain in **dBi** unit. Depending on the argument passed to the constructor in step 2 above, the following keyword argument/arguments is/are to be passed to the method when calculating the antenna gain in any required direction:

*For 'ITUF699' or 'ITUF1245' or 'ITUF1336lg' or 'ITUS465' or 'ITUS580'*

| Keyword| Requirement | Value type   | Range/Option | Description           |
|--|-------------|--------------|--------------|-----------------------|
|`off_axis_angle`| mandatory| `int, float` | `(0, 180)` | off-axis angle (deg.) |

```python
my_antenna.model.gain(off_axis_angle=15.2)
```

*For 'ITUF1336o'*

| Keyword| Requirement | Value type   | Range/Option | Description                                                                           |
|--|-------------|--------------|--------------|---------------------------------------------------------------------------------------|
|`elevation`| mandatory| `int, float` | `(-90, +90)` | elevation angle (deg.) measured from horizontal plane at the site of antenna) |

```python
my_antenna.model.gain(elevation=63.7)
```

*For 'ITUF1336s'*

| Keyword| Requirement | Value type   | Range/Option    | Description                                                                                                   |
|--|-------------|--------------|-----------------|---------------------------------------------------------------------------------------------------------------|
|`azimuth`| mandatory| `int, float` | `(-180, +180)` | Azimuth angle (deg.) in horizontal plane at the site of the antenna measured from the azimuth of maximum gain |
|`elevation`| mandatory| `int, float` | `(-90, +90)`    | Elevation angle (deg.) measured from the horizontal plane) at the site of antenna|

```python
my_antenna.model.gain(azimuth=15.2, elevation=20.4)
```

**Display/store antenna radiation patterns**

In order to display the resulting antenna's radiation patterns, just call `show_patterns()` method of the model used. No argument is required. Once the radiation patterns are displayed, you can store it as an image using the file-save feature of the displaying window.
```python
your_antenna_name.model.show_patterns()
```
**Export antenna parameters to files**

To export the radiation patterns of the antenna and values of the parameters used to model a particular antenna, an Object of relevant Export class needs to be created first. Prior to creating exporter object, you need to import any required exporter class as shown below.
```python
from exporters.csv_export import CSVExport
from exporters.json_export import JSONExport
from exporters.yaml_export import YAMLExport
from exporters.msi_export import MSIExport

your_exporter = ExportClass()
```
Then that object needs to be passed to export() method of the object of your antenna along with the file name you wish the information to be stored. 

```python
your_antenna_name.export(your_exporter, 'path/to/your/file.ext')
```
The following Export Classes are available:

|ExportClass| Description                                    |
|-----------|------------------------------------------------|
|CSVExport()| exports radiation patterns in CSV file format  |
|JSONExport()| exports radiation patterns in JSON file format |
|YAMLExport()| exports radiation patterns in YAML file format|
|MSIExport()| exports radiation patterns in MSI Planet file format|

If you wish to manipulate the data using Excel, you might wish to use CSV exporter. The MSI exporter is particularly good if you wish to use the modelled antenna in the network simulation tools. Many of such tools have functions of importing the radiation patterns from MSI Planet file format. 

Refer to below examples of using exporters:

```python
my_csv_exporter = CSVExport()
my_antenna.export(my_csv_exporter, '../exports/f1336s_ant.csv')

my_json_exporter = JSONExport()
my_antenna.export(my_json_exporter, '../exports/f1336s_ant.json')

my_yaml_exporter = YAMLExport()
my_antenna.export(my_yaml_exporter, '../exports/f1336s_ant.yaml')

my_msi_exporter = MSIExport()
my_antenna.export(my_msi_exporter, '../exports/f1336s_ant.msi')
```

**Modify antenna parameters**

The parameters can be changed any time in the same manner as the initial parameters settings, i.e. calling the `set_params()` method of the model. In below example, the earlier created antenna (refer to step 2 above) for IMT BTS in 1-3 GHz range is re-set to model the TETRA BTS antenna operating in 410-430 MHz range as per the[2] Specifications of antenna model [DB654DG65A-C](https://www.commscope.com/globalassets/digizuite/262332-p360-db654dg65a-c-external.pdf).    
```python
my_antenna.model.set_params(
    oper_freq_mhz=420,  # TETRA Band 0100 center frequency
    max_gain_dbi=15,  # Ref. to [2]
    beamwidth_az_deg=65, # Ref. to [2]
    beamwidth_el_deg=17, # Ref. to [2]
    pattern_type='average',  # [2] is silent on this
    performance_type='improved',  # R[2] is silent on this
    tilt_type='none',  # [1] is neutral on this
)
```

## Project Structure

```
antennas/
│
├── src/                        # Source code/Core logic
│   ├── antenna_models/         # Antenna models
│   ├── exporters/              # Export utilities
│
├── tests/                      # Package testings
├── exports/                    # Exported files
├── docs/                       # Documentation
├── img/                        # Images
├── notebooks/                  # PARAMS testing aid
├── requirements.txt            # Dependencies
├── setup.py                    # Package configuration
├── MANIFEST.in                 # Package add. files
├── README.md                   # Project overview
├── LICENSE.txt                 # License information
└── CONTRIBUTING.md             # Contribution guidelines
```

---

## Contributing

I welcome contributions! See [CONTRIBUTING](CONTRIBUTING.md) for details.

---

## License

This project is licensed under the GNU General Public License. See the [LICENSE](LICENSE.txt) file for details.

---

## Contact

For inquiries or issues, please open an [issue](https://github.com/murzabaevb/antennas/issues) or contact me at b.b.murzabaev @ gmail.com.

---
