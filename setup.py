from setuptools import setup

setup(
    name='getmarcapi',
    packages=['getmarcapi'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'uiucprescon.getmarc2'
    ],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
)
