#!/usr/bin/python3

from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md"), "rb").read().decode("utf-8")


setup(
    name="devpi-testfile",
    description="plugin for devpi that enables direct uploads of tox test result files",
    long_description=README,
    use_scm_version=True,
    url="http://github.com/con-f-use/devpi-testfile",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Programming Language :: Python :: Implementation :: PyPy",
    ]
    + [("Programming Language :: Python :: %s" % x) for x in "3.5 3.6 3.7".split()],
    entry_points={"devpi_client": ["devpi-testfile = devpi_testfile.client"]},
    setup_requires=["setuptools_scm"],
    install_requires=["appdirs", "attrs"],
    extras_require={
        "dev": ["pytest", "pytest-cov"],
        "client": ["devpi-client>=4.3.0"],
        "server": ["devpi-server>=5.0.0"],
    },
    include_package_data=True,
    zip_safe=False,
    options={"bdist_wheel": {"universal": True}},
    python_requires=">=3.5",
    package_dir={"": "src"},
    packages=["devpi_testfile"],
)
