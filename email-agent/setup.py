"""
Setup script for email-agent
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="email-agent",
    version="1.0.0",
    author="Yash Mittal",
    description="Standalone email sending service using Gmail API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "google-auth>=2.16.0",
        "google-auth-oauthlib>=0.8.0",
        "google-auth-httplib2>=0.1.0",
        "google-api-python-client>=2.71.0",
    ],
)
