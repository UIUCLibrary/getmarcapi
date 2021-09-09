import os
import subprocess

from setuptools import setup, Command
import distutils.command.build


class NewBuildCommand(distutils.command.build.build):
    def run(self):
        self.run_command('webpack')
        super(NewBuildCommand, self).run()


class WebPackCommand(Command):
    user_options = []

    def __init__(self, dist, **kw):
        super().__init__(dist, **kw)
        self.output_path = None
        self.node_modules_path = './node_modules'

    def initialize_options(self):
        self.output_path = ''

    def finalize_options(self):
        build_py_command = self.get_finalized_command('build_py')

        self.output_path = os.path.join(
            build_py_command.build_lib,
            'getmarcapi',
            'static'
        )

    def run(self):
        if not os.path.exists(self.node_modules_path):
            command = ['npm', 'install']
            subprocess.check_call(command)

        command = [
            'npm', 'run', 'env', '--',
            'webpack', f'--output-path={self.output_path}'
        ]
        subprocess.check_call(command)


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
    cmdclass={
        'webpack': WebPackCommand,
        'build': NewBuildCommand,
    },

)
