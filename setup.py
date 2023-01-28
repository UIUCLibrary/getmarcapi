import os
import shutil

from setuptools import setup, Command
import distutils.command.build
from distutils.errors import DistutilsExecError


class NewBuildCommand(distutils.command.build.build):
    def run(self):
        self.run_command('webpack')
        super(NewBuildCommand, self).run()


class WebPackCommand(Command):
    description = \
        "compile and bundle javascript source files and dependency libraries"

    user_options = [
        ("inplace", "i", "install javascript files inplace"),
        (
            "npm-path=",
            None,
            "path to npm executable (defaults to one on the path"
        )
    ]

    def __init__(self, dist, **kw):
        super().__init__(dist, **kw)
        self.output_path = None
        self.node_modules_path = './node_modules'
        self.inplace = None
        self.npm_path = None

    def initialize_options(self):
        self.output_path = ''
        self.inplace = None
        self.npm_path = None

    def finalize_options(self):
        if self.npm_path is None:
            self.npm_path = shutil.which('npm')
        build_py_command = self.get_finalized_command('build_py')
        output_root = "" if self.inplace == 1 else build_py_command.build_lib
        self.output_path = os.path.join(
            output_root,
            'getmarcapi',
            'static'
        )

    def run(self):
        if self.npm_path is None or os.path.exists(self.npm_path) is False:
            raise DistutilsExecError(
                "Required program missing from toolchain: npm"
            )
        if not os.path.exists(self.node_modules_path):
            self.announce("Installing npm")
            self.spawn([
                    self.npm_path,
                    'install'
            ])

        command = [
            self.npm_path,
            'run', 'env', '--',
            'webpack', f'--output-path={self.output_path}'
        ]
        self.announce("Running webpack")
        self.spawn(command)

setup(
    packages=['getmarcapi'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'uiucprescon.getmarc2>=0.1.3',
        'typing-extensions;python_version<"3.8"'

    ],
    tests_require=['pytest'],
    setup_requires=['pytest-runner'],
    cmdclass={
        'webpack': WebPackCommand,
        'build': NewBuildCommand,
    },

)
