from setuptools import setup, find_packages

setup(
    name='ps3iso',
    version='0.1',
    url='https://git.sr.ht/~jmstover/ps3iso',
    license='MIT',
    author='Joshua Stover',
    author_email='jmstover6@gmail.com',
    description='CLI tool and Python library for managing Playstation 3 image files',
    packages=find_packages(include=['ps3iso*']),
    entry_points={
        'console_scripts': [
            'ps3iso = ps3iso.__main__:main',
        ]
    },
    python_requires='>=3.6',
    install_requires=[
    ]
)
