"""Setup configuration for MLSENSE."""

from setuptools import setup, find_packages

setup(
    name='mlsense',
    version='2.0.0',
    description='Multi-category sentiment analysis and expert system for product reviews',
    author='Anonymous',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'streamlit>=1.28.0',
        'pandas>=1.5.0',
        'plotly>=5.0.0',
    ],
    python_requires='>=3.8',
)
