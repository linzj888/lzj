#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to check if ABAQUS Python environment is available
"""

import sys

try:
    from odbAccess import openOdb
    from abaqusConstants import *
    print("✓ ABAQUS modules imported successfully")
except ImportError as e:
    print("✗ Error importing ABAQUS modules:", str(e))
    print("Please ensure you are running this script in ABAQUS python environment")
    print("You can run it with:")
    print("  abaqus python test_abaqus_env.py")
    sys.exit(1)

print("✓ ABAQUS Python environment is ready")
sys.exit(0)