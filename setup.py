from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="srt2csv",
    version="0.1",
    packages=find_packages(include=['srt2csv*']),
    py_modules=['subtitle_csv', 'vocabulary'],
    install_requires=requirements,
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'srt2csv=srt2csv.__main__:main',
        ],
    },
    # Include test files
    package_data={
        'tests': ['test_data/*.srt', 'test_data/*.csv', 'test_data/*.txt'],
    },
)

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

setup(
    cmdclass={'test': PyTest},
)
