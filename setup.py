# Automatically created by: scrapyd-deploy

from setuptools import setup, find_packages

setup(
    name='project',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy': ['settings = ithome.settings']},
    include_package_data=True,
    package_data={
        # If any package contains *.json files, include them:
        "libs": ["*.json"],
    }
)
