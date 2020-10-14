from setuptools import setup

setup(
    packages=['getmarcapi'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'uiucprescon.getmarc2>=0.0.1b4'
    ],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
)
