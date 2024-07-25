# Created by Paul Daoudi
# Date: 11/02/2023

from setuptools import setup, find_packages

setup(author='Paul Daoudi',
      name='rllg',
      version='0.1.0',
      packages=find_packages(include=['my_package', 'my_package.*']),
      install_requires=[
            'setuptools==70.3.0',
            'wheel==0.38.0',
            'numpy==1.26.4',
            'torch==2.2.0',
            'tensorboardX==2.4.1',
            'mujoco-py==2.1.2.14',
            'omegaconf==2.1.1',
            'protobuf==3.20.2',
            # Install gym by hand. Works with traditional pip install -e . inside a conda env,
            # but problem with docker otherwise.
            # 'gym==0.21.0',
            'ray[tune]==1.9.2',
            'pyyaml',
            'matplotlib',
            'ipython',
            'pandas',
            'matplotlib',
            'jupyter',
            'ml-collections',
            'scipy',
            # Install dmc2gym by hand, with git clone git+https://github.com/denisyarats/dmc2gym.git and
            # pip install -e .
            'dmc2gym @ git+https://github.com/denisyarats/dmc2gym.git'
      ]
)
