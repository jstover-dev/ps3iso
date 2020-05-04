from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

license = 'MIT'

version = '0.4.0'

name = 'ps3iso'

if __name__ == '__main__':
    setup(
        name=name,
        version=version,
        url='https://git.sr.ht/~jmstover/ps3iso',
        project_urls={
            'Documentation': 'https://ps3iso.readthedocs.io/en/stable',
            'Source': 'https://git.sr.ht/~jmstover/ps3iso',
            'Tracker': 'https://todo.sr.ht/~jmstover/ps3iso',
        },
        license=license,
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
            'Programming Language :: Python :: 3.7',
        ],
    )
