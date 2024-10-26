# setup.py
from setuptools import setup, find_packages

setup(
    name="limoce",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "docker>=5.0.0",
        "aiohttp>=3.8.0",
        "prometheus_client>=0.12.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "pymongo>=3.12.0",
        "psutil>=5.8.0",
        "paramiko>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-asyncio>=0.15.0",
            "pytest-cov>=2.12.0",
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Live Migration of Containers in Edge Computing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/limoce",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
)