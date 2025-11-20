from setuptools import setup, find_packages

setup(
    name="franky-client",
    version="0.1.0",
    description="Remote client for Franky robot control library",
    packages=find_packages(),
    install_requires=[
        "rpyc>=5.0.0",
    ],
    python_requires=">=3.6",
)

