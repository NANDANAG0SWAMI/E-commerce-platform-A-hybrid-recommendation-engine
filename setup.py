from setuptools import setup, find_packages

setup(
    name="Recommendation_poc",
    version="0.1",
    packages=find_packages(),
    package_dir={'': '.'},  # Important for direct installation
)