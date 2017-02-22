from setuptools import setup, find_packages


setup(
    name='etunexus',
    version='0.5.4',
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
    url='http://www.etunexus.com/',
    author='Etu Corporation',
    author_email='indichen@etusolution.com',
    license='GPL',
    packages=find_packages(),
    install_requires=[
        'MultipartPostHandler'
    ],
    zip_safe=False)