# -*- coding: utf-8 -*-
from setuptools import setup
import dolfin


setup(
    name='dolfin',
    version=dolfin.__version__,
    description='A python general purpose utility library',
    long_description=dolfin.__doc__,
    author=dolfin.__author__,
    author_email='hkmshb@gmail.com',
    url='http://hazeltek.com/',
    py_modules=['dolfin'],
    license='MIT',
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Libraries ',
    ],
)
