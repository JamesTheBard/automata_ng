from setuptools import setup, find_packages

setup(name='automatagl',
      version='4.0.2',
      description='A CLI application to create user accounts on Linux systems using different providers (like Gitlab) as a source.',
      author='Jason Weatherly',
      author_email='jamesthebard@gmail.com',
      license='GPLv3',
      packages=find_packages(),
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'automata=automatagl.automatagl:main',
          ],
      },
      install_requires=[
          "certifi==2022.12.7",
          "chardet==3.0.4",
          "idna==2.8",
          "PyYAML",
          "requests==2.22.0",
          "urllib3==1.25.3",
      ],
    )
