## Contributing to Antenna models

Thank you for considering contributing to Antenna models Project! I welcome contributions from the community to improve the project and add more antenna models. Follow these guidelines to get started.

---

### How to Contribute

1. **Fork the repository**: Create your own copy of the repository by forking it.
2. **Clone the repository**: Clone your forked repository to your local machine:
   ```bash
   git clone https://github.com/murzabaevb/antennas.git
   cd antennas
   ```
3. **Create a new branch**: Make a branch for your feature or bugfix:
   ```bash
   git checkout -b feature-name
   ```
4. **Make changes**: Add your code, documentation, or tests.
5. **Test your changes**: Ensure that your code is tested and passes all checks.
6. **Commit your changes**: Write a clear and concise commit message:
   ```bash
   git commit -m "Add feature or fix bug"
   ```
7. **Push your branch**: Push your changes to your forked repository:
   ```bash
   git push origin feature-name
   ```
8. **Submit a pull request**: Open a pull request from your branch to the main repository's `main` branch.

---

### Guidelines

- Follow the project's coding style.
- Add or update tests for any new functionality or fixes.
- Update the documentation if necessary.
- Be respectful and collaborative in discussions.

---

### Reporting Issues

If you find a bug or have a suggestion, open an [issue](https://github.com/murzabaevb/antennas/issues) and provide as much detail as possible.

---

### Adding New Antenna Models

To contribute a new antenna model to the project, you need to follow these guidelines. The project is structured around a `BaseAntennaModel` class, which defines the interface and core behavior for all antenna models.

#### **Overview of Main Classes**

1. **`BaseAntenna`** (Located in `src/antenna/base.py`)
   - **Purpose**: Serves as the base class for all antenna models.
   - **Key Responsibilities**:
     - Provide a consistent structure for all models.
     - Handle common functionalities like validation of constructor's parameters,displaying radiation patterns, exporting data.

   - **Main Methods**:
     - `set_params()`: Validate the passed **kwargs as the antenna settings in accordance with the `PARAMS` dictionary of chosen antenna model class.
     - `_post_set_params()`: This is a hook for subclasses to set dependent parameters in case if functionality of `set_params()` is not enough. The subclass can rewrite it. It is invoked automatically at the end of `set_params()` method.
     - `show_patterns()`: Displays the antenna radiation patterns as per the `specs` property of the object.
     - `export()`: Exports the antenna radiation data contained in the `specs` property of the object to a file in the specified format (e.g. CSV, JSON, MSI).
     - `_update_specs()`: Abstract method to be implemented in subclasses. Updates the `specs` property of the object. It is invoked automatically at the beginning of `show_patterns()` and `export()` methods.
     - `gain()`: Abstract method to be implemented in subclasses. Returns the antenna gain at the angle/angles passed to the function as keyword arguments.
     

2. **Antenna Models** (e.g., `ITUF699`, `ITUF1245` etc., located in `src/antenna/antenna_models/`)
   - **Purpose**: Implement specific antenna model based on ITU-R Recommendation.
   - **Expected Properties**:
   - `PARAMS` : dictionary. Set of mandatory, conditional and optional keyword arguments, value types and their ranges used for setting the specifications of the antenna.
   - **Expected Methods**:
     - Override the `_post_set_params()` method if basic validation implemented in `set_params()` method of `BaseAntenna` class is not enough or some dependent object's properties must be set.
     - Implement `_update_specs()` method in the subclass. The method shall populate/update the `specs` property/dictionary of the object with values only. It is expected that `h_pattern_datapoint` and `v_pattern_datapoint` are done in 1 degree step from 0 to 360 (inclusive).
     - Implement the `gain()` method in the subclass. It must return the antenna gain (dBi) in the direction passed as argument to the method.

#### **Steps to Add a New Model**

1. **Create a New Class**:
   - Place the new class in the `src/antenna/antenna_models/` directory.
   - Inherit from `BaseAntenna`.

   ```python
   from antenna.base import BaseAntenna

   class NewAntennaModel(BaseAntenna):
        def __init__(self):
            super().__init__()
   ```

2. **Define Parameters**:
   - Define the `PARAMS` dictionary of the `NewAntennaModel`. Look for implemented antenna model classes for examples.

3. **Override `_post_set_params()` if needed**
   
    Do it only if necessary 

4. **Implement `_update_specs()` method**
    In doing so, don't change the keywords of `specs` property-dictionary of the `BaseAntenna` class, but just fill it by values in the correct units.
5. **Implement `gain(self, **kwargs)` method**
    In part of validation of **kwargs in this method, you might find code-lines of existing classes useful. If so, you need to amend only the `required_keys` dictionary without modifying the rest of below shown snippet. 
```python
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
```
6. **Document the Model**:
   - Update the `README.md` with details about the new model.
   - Include usage examples for users.

