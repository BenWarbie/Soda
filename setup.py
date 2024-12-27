from setuptools import setup, find_packages

setup(
    name="solana-trading-bot",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "solders>=0.18.1,<0.19.0",  # Must be installed before solana
        "solana==0.30.2",  # Pin exact version to match requirements.txt
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.1",
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1",
        "pytest-cov>=4.1.0",
        "coverage>=7.3.2",
    ],
    python_requires=">=3.10,<3.11",
    author="Ben",
    description="Terminal-based multi-wallet trading bot for Solana blockchain",
)
