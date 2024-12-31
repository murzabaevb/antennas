from setuptools import setup, find_packages

setup(
    name="antennas",
    version="1.0.0",
    description='ITU-R antenna models',
    long_description='Provides functions for calculation of antenna gains, displaying radiation patterns and their exports',
    author='Bakyt-Bek Murzabaev',
    author_email='b.b.murzabaev@gmail.com',
    url='https://github.com/murzabaevb/antennas.git',
    download_url='https://github.com/murzabaevb/antennas.git',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    license='GNU General Public License',
    license_files='https://www.gnu.org/licenses/',
    keywords='itu,itu-r,antenna,pattern,gain,699,1245,1336',
)
