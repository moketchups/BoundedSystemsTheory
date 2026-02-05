"""
HSAP - Human Source Attestation Protocol

Setup script for packaging and installation.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="hsap",
    version="1.0.0",
    author="AI Consensus Team",
    author_email="hsap@example.com",
    description="Human Source Attestation Protocol - Prevent AI model collapse through data provenance tracking",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hsap/hsap",
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=42.0.0",
        "click>=8.0.0",
    ],
    extras_require={
        "pytorch": [
            "torch>=2.0.0",
        ],
        "viz": [
            "networkx>=3.0",
            "matplotlib>=3.5.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "all": [
            "torch>=2.0.0",
            "networkx>=3.0",
            "matplotlib>=3.5.0",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hsap=hsap.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
