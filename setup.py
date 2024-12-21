from setuptools import setup, find_packages

setup(
    name="antenna",
    version="0.1.0",
    description='ITU antenna models',
    author='Bakyt-Bek Murzabaev',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
