from setuptools import setup

PACKAGE = 'ChangesetValidator'
VERSION = '0.1'

setup(
    name=PACKAGE,
    version=VERSION,
    description='Changeset validation routines',
    author="IT Attractor",
    author_email="info@it-attractor.com",
    license='',
    url='',
    packages=['changesetvalidator'],
    entry_points={
        'trac.plugins': [
            'changesetvalidator.command = changesetvalidator.command',
        ]
    },
    package_data={
        'changesetvalidator': [],
    }
)
