from setuptools import setup, find_packages

# Read description
with open("README.md", "r") as readme:
    README_TEXT = readme.read()

with open(".env", "r") as fenv:
    lines = fenv.readlines()
    VERSION = lines[1].strip().split("=")[1]

# main setup configuration class
setup(
    name="sim_cmcl_mods_wrapper",
    version=VERSION,
    author="CMCL Innovations",
    description="The MoDS-OSP wrapper",
    keywords="CMCL, MoDS, SimPhoNy, cuds, sample",
    long_description=README_TEXT,
    install_requires=[
        "osp-core==3.6.0",
    ],
    packages=find_packages(exclude=["mods_mock_agent"]),
    test_suite="tests",
    entry_points={
        "wrappers": "wrapper = osp.wrappers.sim_cmcl_mods_wrapper:mods_session"
    },
)
