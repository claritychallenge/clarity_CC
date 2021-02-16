import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="clarity_core",
    version="0.0.1",
    author="Jon Barker",
    author_email="j.p.barker@sheffield.ac.uk",
    description="Core utilities for the Clarity project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://https://github.com/claritychallenge/clarity",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
