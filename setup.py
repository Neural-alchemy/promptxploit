from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="promptxploit",
    version="1.0.0",
    author="Neural Alchemy",
    author_email="contact@neuralalchemy.ai",
    description="LLM penetration testing framework - Discover vulnerabilities before attackers do",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Neural-alchemy/promptxploit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "rich",  # Pretty terminal output
        "openai",  # For adaptive API mode (optional)
        "anthropic",  # For Claude adaptive mode (optional)
    ],
    extras_require={
        "dev": ["pytest", "black", "flake8"],
        "local": ["llama-cpp-python"],  # For local LLM adaptive mode
    },
    include_package_data=True,
    package_data={
        "promptxploit": ["attacks/**/*.json"],
    },
    entry_points={
        "console_scripts": [
            "promptxploit=promptxploit.main:main",
        ],
    },
)
