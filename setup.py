from setuptools import setup, find_packages

setup(
    name="srt2csv",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Add any dependencies here if needed
    ],
    entry_points={
        'console_scripts': [
            'srt2csv=srt2csv.__main__:main',
        ],
    },
)
