import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="r2p2py",
    version=0.24,
    author="robin hayman",
    author_email="robin.hayman@gmail.com",
    description="Analysis of 2P data",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/rhayman/r2p2py",
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={"": ["*.txt"]},
    install_requires=[
        "numpy",
        "matplotlib"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
