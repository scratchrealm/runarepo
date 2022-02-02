from setuptools import setup, find_packages

setup(
    packages=find_packages(),
    scripts=['bin/runarepo'],
    include_package_data = True,
    install_requires=[
        'kachery-client>=1.0.21'
    ]
)
