from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='ps3iso',
    version='0.3.1',
    url='https://git.sr.ht/~jmstover/ps3iso',
    license='MIT',
    author='Joshua Stover',
    author_email='jmstover6@gmail.com',
    description='CLI tool and Python library for managing Playstation 3 image files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(include=['ps3iso*']),
    entry_points={
        'console_scripts': [
            'ps3iso = ps3iso.__main__:main',
        ]
    },
    python_requires='>=3.6',
    install_requires=[
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
