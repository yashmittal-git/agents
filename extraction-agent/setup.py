from setuptools import setup, find_packages

setup(
    name="extraction-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "requests>=2.31.0",
        "PyPDF2>=3.0.0",
    ],
    author="Yash Mittal",
    description="Universal content extraction service using AI",
    python_requires=">=3.9",
)
