# coding=utf-8
from setuptools import setup



setup(name='preTeX',
      version="0.2.1",
      packages=['pretex'],
      entry_points={
           'console_scripts': [
               'pretex = pretex.pretex:main',
           ],
        },
      author='Sebastian Werhausen',
      author_email="swerhausen@gmail.com",
      url='https://github.com/s9w/preTeX',
      description="LaTeX preprocessor to simplify math typesetting",)