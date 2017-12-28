from setuptools import setup, find_packages

setup(
    name='cleansweep',
    version='0.1.0',
    description='A bot that cleans up on instantly profitable extant EtherDelta orders',
    # url - not sure if I'll add this or not
    author='Max Shenfield',
    author_email='shenfieldmax@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: CryptoCurrency',
        'Topic :: Software Development :: Finance',
        # 'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='etherdelta exchange arbitrage bot',
    packages=find_packages(
        exclude=['tests'],
    ),
    install_requires=[
        'attrs',
        'ratelimiter',
        'socketIO_client_nexus',
    ],
    extras_require={  # Optional
        'dev': ['ipython', 'ipdb'],
        'test': ['pytest'],
    },
    # Might need to include for specific markets
    # package_data={
    #     'sample': ['package_data.dat'],
    # },
    entry_points={
        'console_scripts': [
            'cleansweep=cleansweep.cli:main',
        ],
    },
)
