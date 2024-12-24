from setuptools import setup, find_packages

setup(
    name="solana-trading-bot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "solana>=0.30.2",
        "web3>=6.11.1",
        "python-dotenv>=1.0.0",
        "aiohttp>=3.9.1",
    ],
    python_requires=">=3.10,<3.11",
    author="Ben",
    description="Multi-wallet trading bot for Solana blockchain",
)
