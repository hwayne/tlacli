from setuptools import setup, find_packages

setup(name="tlacli", 
        packages=find_packages("src"),
        package_dir={"":"src"},
        entry_points={
            'console_scripts': ["tlacli=tlacli.tlacli:main"]
            })
