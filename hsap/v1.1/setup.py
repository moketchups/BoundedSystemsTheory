"""
HSAP v1.1 - Human Source Attestation Protocol (Scalable MVP)
"""

from setuptools import setup, find_packages

setup(
    name="hsap",
    version="1.1.0",
    author="7-AI Consensus Team",
    description="Human Source Attestation Protocol - Prevent AI model collapse",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "click>=8.0.0",
        "cryptography>=42.0.0",
        "requests>=2.31.0",
    ],
    extras_require={
        "registry": [
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.27.0",
            "asyncpg>=0.29.0",
            "aiohttp>=3.9.0",
            "aiodns>=3.1.0",
        ],
        "all": [
            "fastapi>=0.109.0",
            "uvicorn[standard]>=0.27.0",
            "asyncpg>=0.29.0",
            "aiohttp>=3.9.0",
            "aiodns>=3.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hsap=cli.hsap_cli:cli",
        ],
    },
)
