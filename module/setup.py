from setuptools import setup, find_packages

import etunexus

setup(
    name='etunexus',
    version=etunexus.__version__,
    description='Etu Nexus API',
    long_description=open("README.rst").read(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Intended Audience :: Developers',
    ],
    url=etunexus.__url__,
    author=etunexus.__author__,
    author_email=etunexus.__author_email__,
    license=etunexus.__license__,
    packages=find_packages(),
    install_requires=[
        'MultipartPostHandler'
    ],
    zip_safe=False)