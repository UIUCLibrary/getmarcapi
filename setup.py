from setuptools import setup

setup(
    packages=['getmarcapi'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'uiucprescon.getmarc2>=0.1.0b4',
        'typing-extensions;python_version<"3.8"'

    ],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
)
