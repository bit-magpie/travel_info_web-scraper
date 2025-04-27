from setuptools import setup, find_packages

setup(
    name="travel_app",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here, e.g., Flask, requests, etc.
    ],
    entry_points={
        "console_scripts": [
            "travel_app=travel_app.main:main",
        ],
    },
)