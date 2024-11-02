# Cloud Format Converter

A Python tool to convert between Terraform (HCL) and CloudFormation (YAML/JSON) formats. This tool supports bidirectional conversion with full support for variables, outputs, dependencies, and provider configurations.

## Features

- Convert Terraform (HCL) to CloudFormation (YAML/JSON)
- Convert CloudFormation to Terraform
- Support for:
  - Variables and parameters
  - Output values
  - Dependencies and references
  - Provider-specific configurations
  - Rich resource type mappings
  - Template validation

## Installation

```bash
# From PyPI (when published)
pip install cloud-format-converter

# From source
git clone https://github.com/brokosz/cloud-format-converter.git
cd cloud-format-converter
pip install -e ".[dev]"
```

## Usage

### Command Line Interface

1. Convert Terraform to CloudFormation:
```bash
cloud-format convert input.tf output.yaml
```

2. Convert CloudFormation to Terraform:
```bash
cloud-format convert template.yaml output.tf --format tf
```

3. Convert and output as JSON:
```bash
cloud-format convert input.tf template.json --output-format json
```

4. Validate a template:
```bash
cloud-format validate template.yaml --type cloudformation
```

5. Use with pipes:
```bash
cat main.tf | cloud-format convert - - --format cf > template.yaml
```

### Python API

```python
from cloud_format_converter import CloudFormatConverter

# Initialize the converter
converter = CloudFormatConverter()

# Convert Terraform to CloudFormation
with open('main.tf', 'r') as f:
    tf_content = f.read()
cf_template = converter.tf_to_cf(tf_content)

# Convert CloudFormation to Terraform
with open('template.yaml', 'r') as f:
    cf_content = f.read()
tf_config = converter.cf_to_tf(cf_content)
```

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Run tests:
```bash
pytest
```

4. Run linting:
```bash
flake8 src tests
black src tests
```

### Adding New Resource Types

To add support for new AWS resource types:

1. Add the mapping to `resource_type_mappings` in `converter.py`:
```python
self.resource_type_mappings = {
    "AWS::NewService::Resource": "aws_new_service_resource",
    # ...
}
```

2. Add any necessary property transformations in the conversion methods.

## Contributing

1. Fork the repository
2. Create a feature branch:
```bash
git checkout -b feature/new-feature
```

3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- For bugs and features, please create an issue in the GitHub repository
- For security issues, please see SECURITY.md
- For general questions, please use GitHub Discussions

## Acknowledgments

- Thanks to the Python community for great tools like `python-hcl2` and `pyyaml`
- Inspired by the need to maintain infrastructure as code in multi-tool environments