from setuptools import setup, find_packages

setup(name="tlacli", 
        packages=find_packages("src"),
        package_dir={"":"src"},
        package_data={"tlacli": ["tla2tools.jar"]},
        entry_points={
            'console_scripts': ["tlacli=tlacli.tlacli:main"]
            })
