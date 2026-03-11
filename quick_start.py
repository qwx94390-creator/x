# Quick Start Script

"""
This script automates the environment setup and application launching.
"""

import os
import subprocess


def setup_environment():
    # Add your environment setup code here
    print("Setting up the environment...")
    # For example, install dependencies
    subprocess.run(["pip", "install", "-r", "requirements.txt"])


def launch_application():
    # Add your application launching code here
    print("Launching the application...")
    subprocess.run(["python", "app.py"])


def main():
    setup_environment()
    launch_application()


if __name__ == '__main__':
    main()