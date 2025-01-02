from setuptools import setup, find_packages

setup(
    name="antennas",
    version="1.1.0",
    description='ITU-R antenna models',
    long_description='Provides functions for calculation of antenna gains, displaying radiation patterns and their exports',
    author='Bakyt-Bek Murzabaev',
    author_email='b.b.murzabaev@gmail.com',
    url='https://github.com/murzabaevb/antennas.git',
    download_url='https://github.com/murzabaevb/antennas.git',
    packages=find_packages(where="src"),  # Discover packages under src/
    package_dir={"": "src"},  # Map package directory root to src/
    include_package_data=True,  # Include additional files specified in MANIFEST.in
    package_data={
        "": ["antenna_models/*", "exporter/*"],  # Include both antenna_models and exporter
    },
    license='GNU General Public License',
    license_files='https://www.gnu.org/licenses/',
    keywords='itu,itu-r,antenna,pattern,gain,699,1245,1336',
)

