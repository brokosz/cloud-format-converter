# Cloud Format Converter

A Python tool to convert between Terraform and CloudFormation formats. This tool supports bidirectional conversion with full support for variables, outputs, dependencies, and provider configurations.

## Features

- Convert Terraform (HCL) to CloudFormation (YAML/JSON)
- Convert CloudFormation to Terraform
- Support for variables and parameters
- Support for output values
- Handle dependencies and references
- Provider-specific configurations
- Rich resource type mappings
- Template validation

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cloud-format-converter
cd cloud-format-converter

# Install in development mode
pip install -e .
```

## Usage

### Command Line Interface

1. Convert Terraform to CloudFormation:
```bash
cloud-format convert main.tf template.yaml
```

2. Convert CloudFormation to Terraform:
```bash
cloud-format convert template.yaml output.tf --format tf
```

3. Convert and output as JSON:
```bash
cloud-format convert main.tf template.json --output-format json
```

4. Validate a template:
```bash
cloud-format convert validate template.yaml --type cloudformation
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

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
