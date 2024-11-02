#!/usr/bin/env python3

import argparse
import sys
import json
import yaml
from pathlib import Path
from typing import Optional, Union
from cloud_format_converter import CloudFormatConverter  # Import the previous converter class


class CloudFormatCLI:
    def __init__(self):
        self.converter = CloudFormatConverter()

    def setup_parser(self) -> argparse.ArgumentParser:
        """Set up command line argument parser"""
        parser = argparse.ArgumentParser(
            description="Convert between Terraform and CloudFormation formats",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
    # Convert Terraform to CloudFormation (auto-detects format)
    %(prog)s convert input.tf output.yaml
    
    # Convert CloudFormation to Terraform
    %(prog)s convert template.yaml output.tf --format tf
    
    # Convert and specify output format
    %(prog)s convert input.tf output.json --output-format json
    
    # Validate a template
    %(prog)s validate template.yaml --type cloudformation
    
    # Convert stdin to stdout
    cat input.tf | %(prog)s convert - - --format cf
            """,
        )

        subparsers = parser.add_subparsers(dest="command", help="Available commands")

        # Convert command
        convert_parser = subparsers.add_parser("convert", help="Convert between formats")
        convert_parser.add_argument("input", help="Input file (or - for stdin)")
        convert_parser.add_argument("output", help="Output file (or - for stdout)")
        convert_parser.add_argument(
            "--format",
            choices=["tf", "cf"],
            help="Target format (tf=Terraform, cf=CloudFormation). If not specified, will be detected from file extension",
        )
        convert_parser.add_argument(
            "--output-format",
            choices=["json", "yaml"],
            help="Output format for CloudFormation (default: yaml)",
        )

        # Validate command
        validate_parser = subparsers.add_parser("validate", help="Validate template format")
        validate_parser.add_argument("input", help="Input file to validate")
        validate_parser.add_argument(
            "--type",
            choices=["terraform", "cloudformation"],
            required=True,
            help="Template type to validate against",
        )

        return parser

    def read_input(self, input_path: str) -> str:
        """Read input from file or stdin"""
        if input_path == "-":
            return sys.stdin.read()
        else:
            with open(input_path, "r") as f:
                return f.read()

    def write_output(
        self, output_path: str, content: Union[str, dict], output_format: Optional[str] = None
    ) -> None:
        """Write output to file or stdout"""
        if isinstance(content, dict):
            if output_format == "json":
                output_content = json.dumps(content, indent=2)
            else:  # yaml
                output_content = yaml.dump(content, default_flow_style=False)
        else:
            output_content = content

        if output_path == "-":
            print(output_content)
        else:
            with open(output_path, "w") as f:
                f.write(output_content)

    def detect_format(self, file_path: str) -> str:
        """Detect format from file extension"""
        if file_path == "-":
            raise ValueError("Cannot detect format from stdin, please specify --format")

        ext = Path(file_path).suffix.lower()
        if ext in [".tf", ".tfvars"]:
            return "tf"
        elif ext in [".yaml", ".yml", ".json"]:
            return "cf"
        else:
            raise ValueError(f"Cannot detect format from extension: {ext}")

    def convert(self, args: argparse.Namespace) -> None:
        """Handle convert command"""
        # Read input
        input_content = self.read_input(args.input)

        # Determine target format
        target_format = args.format
        if not target_format:
            try:
                target_format = "cf" if self.detect_format(args.input) == "tf" else "tf"
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)

        try:
            # Convert content
            if target_format == "cf":
                result = self.converter.tf_to_cf(input_content)
                self.write_output(args.output, result, args.output_format)
            else:  # tf
                result = self.converter.cf_to_tf(input_content)
                self.write_output(args.output, result)

        except Exception as e:
            print(f"Error during conversion: {e}", file=sys.stderr)
            sys.exit(1)

    def validate(self, args: argparse.Namespace) -> None:
        """Handle validate command"""
        try:
            input_content = self.read_input(args.input)
            if args.type == "terraform":
                self.converter.validate_conversion(input_content, "terraform")
            else:  # cloudformation
                self.converter.validate_conversion(input_content, "cloudformation")
            print("Validation successful!")
        except Exception as e:
            print(f"Validation failed: {e}", file=sys.stderr)
            sys.exit(1)

    def run(self) -> None:
        """Run the CLI application"""
        parser = self.setup_parser()
        args = parser.parse_args()

        if args.command == "convert":
            self.convert(args)
        elif args.command == "validate":
            self.validate(args)
        else:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    cli = CloudFormatCLI()
    cli.run()


def main():
    cli = CloudFormatCLI()
    cli.run()


if __name__ == "__main__":
    main()
