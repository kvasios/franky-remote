from setuptools import setup, find_packages

setup(
    name="franky-client",
    version="0.1.0",
    description="Remote client for Franky robot control library",
    packages=find_packages(where="client"),
    package_dir={"": "client"},
    install_requires=[
        "rpyc>=5.0.0",
    ],
    python_requires=">=3.6",
)

