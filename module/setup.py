from setuptools import setup, find_packages

setup(name='etunexus',
      version='1.0',
      description='Etu Nexus API',
      url='http://www.etunexus.com/',
      author='Etu Corporation',
      author_email='',
      license='GPL',
      packages=find_packages(),
      install_requires=[
            'MultipartPostHandler',
      ],
      zip_safe=False)