# coding=utf-8
from setuptools import setup

setup(name='preTeX',
      version="0.5.0",
      include_package_data=True,
      packages=['pretex'],
      package_data={
          'pretex': ['viz/script.js', 'viz/style.css']
      },
      entry_points={
          'console_scripts': [
              'pretex = pretex.pretex:main',
          ],
      },
      author='Sebastian Werhausen',
      author_email="swerhausen@gmail.com",
      url='https://github.com/s9w/preTeX',
      description="LaTeX preprocessor to simplify math typesetting")