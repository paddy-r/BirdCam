''' HR 01/05/23 Basic setup for testing '''

from setuptools import setup, find_packages
import sys
sys.path.append(".")
setup(name='birdcam',
      version='2.1.0',
      packages=find_packages(include=['birdcam', 'birdcam.*',
                                      'images', 'images.*']),
      install_requires=[])
