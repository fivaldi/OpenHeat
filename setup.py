from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setup(
    name='OpenHeat',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    entry_points='''
        [console_scripts]
        openheat=openheat.openheat:cli
    ''',
)
