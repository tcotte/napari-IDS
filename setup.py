#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


# requirements = []
# with open('requirements.txt') as f:
#     for line in f:
#         stripped = line.split("#")[0].strip()
#         if len(stripped) > 0:
#             requirements.append(stripped)


# https://github.com/pypa/setuptools_scm
use_scm = {"write_to": "napari_IDS/_version.py"}

setup(
    name='napari_IDS',
    author='Tristan Cotte',
    author_email='tristan.cotte@sgs.com',
    license='BSD-3',
    url='https://github.com/tcotte/napari-IDS',
    description='Plug in which enables to take photo with IDS uEye camera',
    long_description_content_type='text/markdown',
    long_description="file: README.md",
    packages=find_packages(),
    python_requires='>=3.8',
    # install_requires=requirements,
    install_requires=['opencv-python', 'numpy'],
    use_scm_version=use_scm,
    version="0.0.2",
    setup_requires=['setuptools_scm'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Framework :: napari',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
    ],
)