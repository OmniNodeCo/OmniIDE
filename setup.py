from setuptools import setup, find_packages

setup(
    name="OmniIDE",
    version="1.0.0",
    author="OmniNodeCo",
    description="A fast, modern, lightweight desktop IDE",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "ttkbootstrap>=1.10.1",
    ],
    entry_points={
        "console_scripts": [
            "omniide=run:main",
        ],
    },
)