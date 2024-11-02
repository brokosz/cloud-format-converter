from setuptools import setup, find_packages

setup(
    name="cloud-format-converter",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=5.1",
        "python-hcl2>=2.0",
    ],
    entry_points={
        "console_scripts": [
            "cloud-format=cloud_format_cli:CloudFormatCLI().run",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool to convert between Terraform and CloudFormation formats",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/cloud-format-converter",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)