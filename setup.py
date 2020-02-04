from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tlacli", 
    version="0.0.1",
    author="Hillel Wayne",
    author_email="h@hillelwayne.com",
    description="A wrapper script for running TLA+ from the command line",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hwayne/tlacli",
    packages=find_packages("src"),
    package_dir={"":"src"},
    package_data={"tlacli": ["tla2tools.jar"]},
    python_requires='>=3.7',
    entry_points={
        'console_scripts': ["tlacli=tlacli.tlacli:main"]
        },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Java Libraries", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
