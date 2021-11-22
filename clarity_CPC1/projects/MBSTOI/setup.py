import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MBSTOI",
    version="0.0.1",
    author="Clarity Team",
    author_email="contact@claritychallenge.org",
    description="Intelligibility model for the Clarity project",
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
