#!/usr/bin/env python3
"""
Package generated simulation input files and design points into a ZIP archive.

This script creates a ZIP package containing all generated input files
and the design points CSV file for easy download.

Usage:
    python package_outputs.py --input-dir <input_directory> --csv <design_points_csv> --output <output_zip>
"""

import argparse
import zipfile
from pathlib import Path
import shutil


class OutputPackager:
    """Package generated simulation input files into a ZIP archive."""

    def __init__(self, input_dir: str, csv_file: str, output_zip: str):
        self.input_dir = Path(input_dir)
        self.csv_file = Path(csv_file)
        self.output_zip = Path(output_zip)

    def validate_inputs(self):
        """Validate input files and directories."""
        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")

        if not self.csv_file.exists():
            raise FileNotFoundError(f"Design points CSV file not found: {self.csv_file}")

        # Check if input directory contains any files
        input_files = list(self.input_dir.glob('*.*'))
        if not input_files:
            raise ValueError(f"No input files found in directory: {self.input_dir}")

    def create_package(self):
        """Create ZIP package containing all files."""
        self.validate_inputs()

        # Create output directory if needed
        self.output_zip.parent.mkdir(parents=True, exist_ok=True)

        # Get list of files to package
        input_files = list(self.input_dir.glob('*.*'))

        print(f"Packaging {len(input_files)} input files and CSV...")
        print(f"Input directory: {self.input_dir}")
        print(f"CSV file: {self.csv_file}")
        print(f"Output ZIP: {self.output_zip}")

        # Create ZIP file
        with zipfile.ZipFile(self.output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add input files
            for input_file in input_files:
                if input_file.is_file():
                    arcname = input_file.name
                    zipf.write(input_file, arcname)
                    print(f"  Added: {arcname}")

            # Add CSV file
            arcname = self.csv_file.name
            zipf.write(self.csv_file, arcname)
            print(f"  Added: {arcname}")

        # Get file size
        zip_size = self.output_zip.stat().st_size
        size_mb = zip_size / (1024 * 1024)

        print(f"\n✅ Successfully created package: {self.output_zip}")
        print(f"   File size: {size_mb:.2f} MB")

        return {
            'zip_file': str(self.output_zip),
            'input_files_count': len(input_files),
            'total_files': len(input_files) + 1,
            'size_mb': size_mb
        }


def main():
    parser = argparse.ArgumentParser(
        description='Package generated simulation input files and design points into ZIP'
    )
    parser.add_argument(
        '--input-dir',
        required=True,
        help='Directory containing generated input files'
    )
    parser.add_argument(
        '--csv',
        required=True,
        help='Design points CSV file'
    )
    parser.add_argument(
        '--output',
        default='simulation_inputs.zip',
        help='Output ZIP file path (default: simulation_inputs.zip)'
    )

    args = parser.parse_args()

    packager = OutputPackager(args.input_dir, args.csv, args.output)
    result = packager.create_package()

    print(f"\nPackage summary:")
    print(f"  Input files: {result['input_files_count']}")
    print(f"  Total files: {result['total_files']}")
    print(f"  Size: {result['size_mb']:.2f} MB")
    print(f"  Location: {result['zip_file']}")


if __name__ == '__main__':
    main()
