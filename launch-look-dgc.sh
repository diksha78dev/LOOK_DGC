#!/bin/bash

echo "================================================"
echo "  LOOK-DGC - Digital Image Forensics Toolkit"
echo "  Developed by: Gopichand"
echo "================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.11 or later"
    exit 1
fi

# Check if gui directory exists
if [ ! -d "gui" ]; then
    echo "Error: GUI directory not found"
    echo "Please ensure you are running this from the LOOK-DGC root directory"
    exit 1
fi

# Launch LOOK-DGC
echo "Starting LOOK-DGC..."
python3 launch_look_dgc.py

echo
echo "LOOK-DGC has closed."