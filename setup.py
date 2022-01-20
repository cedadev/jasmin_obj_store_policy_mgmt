#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

__author__ = "Philip Kershaw"
__contact__ = "philip.kershaw@stfc.ac.uk"
__copyright__ = "Copyright 2020 United Kingdom Research and Innovation"
__license__ = "BSD - see LICENSE file in top-level package directory"

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = [line.strip() for line in open("requirements.txt")]

dev_requirements = [line.strip() for line in open("requirements_dev.txt")]

test_requirements = [
    "pytest>=3",
]

docs_requirements = [
    "sphinx",
    "sphinx-rtd-theme",
    "nbsphinx",
    "pandoc",
    "ipython",
    "ipykernel",
    "jupyter_client",
]

setup(
    author=__author__,
    author_email=__contact__,
    python_requires=">=3.6",
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Security",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Distributed Computing",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    description="Manage access policies for JASMIN Object Store",
    entry_points={
        "console_scripts": [
            "jasmin_obj_store_policy=jasmin.obj_store.policy_mgmt.cli:main",
        ],
    },
    install_requires=requirements,
    license=__license__,
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="jasmin_obj_store_policy_mgmt",
    name="jasmin_obj_store_policy_mgmt",
    packages=find_packages(),
    test_suite="tests",
    tests_require=test_requirements,
    extras_require={"docs": docs_requirements, "dev": dev_requirements},
    url="https://github.com/philipkershaw/jasmin_obj_store_policy_mgmt",
    zip_safe=False,
)
