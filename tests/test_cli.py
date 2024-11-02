import pytest
from cloud_format_converter.cli import CloudFormatCLI
import tempfile
import os

@pytest.fixture
def cli():
    return CloudFormatCLI()

@pytest.fixture
def temp_tf_file():
    content = """
    resource "aws_s3_bucket" "example" {
      bucket = "my-test-bucket"
    }
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
        f.write(content)
        return f.name

@pytest.fixture
def temp_cf_file():
    content = """
    Resources:
      MyBucket:
        Type: AWS::S3::Bucket
        Properties:
          BucketName: my-test-bucket
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(content)
        return f.name

def test_convert_tf_to_cf(cli, temp_tf_file, tmp_path):
    output_file = os.path.join(tmp_path, "output.yaml")
    args = type('Args', (), {
        'input': temp_tf_file,
        'output': output_file,
        'format': 'cf',
        'output_format': 'yaml'
    })()
    
    cli.convert(args)
    assert os.path.exists(output_file)
    
    with open(output_file, 'r') as f:
        content = f.read()
        assert 'AWS::S3::Bucket' in content

def test_convert_cf_to_tf(cli, temp_cf_file, tmp_path):
    output_file = os.path.join(tmp_path, "output.tf")
    args = type('Args', (), {
        'input': temp_cf_file,
        'output': output_file,
        'format': 'tf',
        'output_format': None
    })()
    
    cli.convert(args)
    assert os.path.exists(output_file)
    
    with open(output_file, 'r') as f:
        content = f.read()
        assert 'aws_s3_bucket' in content