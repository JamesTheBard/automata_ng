from setuptools import setup, find_packages

setup(name='automatagl',
      version='3.0.1',
      description='A CLI application to create user accounts on Linux systems from Gitlab users/group information.',
      author='Jason Weatherly',
      author_email='jason.weatherly@myquestis.com',
      license='GPLv3',
      packages=find_packages(),
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'automata=automatagl.automatagl:main',
          ],
      },
      install_requires=[
          "certifi==2019.3.9",
          "chardet==3.0.4",
          "idna==2.8",
          "PyYAML",
          "requests==2.22.0",
          "urllib3==1.25.3",
      ],
    )
