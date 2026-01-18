"""Setup configuration for Python Codebase Reviewer."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = [
    "google-adk>=0.1.0",
    "requests>=2.31.0",
]

dev_requirements = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.12.0",
    "pytest-timeout>=2.2.0",
    "black>=23.12.0",
    "flake8>=7.0.0",
    "mypy>=1.8.0",
]

setup(
    name="python-codebase-reviewer",
    version="0.1.0",
    author="ADK Team",
    author_email="",
    description="AI-powered Python code review using multi-agent system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pavanpaik/agents-with-adk",
    project_urls={
        "Bug Tracker": "https://github.com/pavanpaik/agents-with-adk/issues",
        "Documentation": "https://github.com/pavanpaik/agents-with-adk/tree/main/docs",
        "Source Code": "https://github.com/pavanpaik/agents-with-adk",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "github": ["flask>=3.0.0", "PyJWT>=2.8.0", "cryptography>=41.0.0"],
    },
    include_package_data=True,
    zip_safe=False,
)
