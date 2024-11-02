import pytest
from cloud_format_converter.converter import CloudFormatConverter

def test_tf_to_cf_basic_s3():
    converter = CloudFormatConverter()
    tf_content = """
    resource "aws_s3_bucket" "example" {
      bucket = "my-test-bucket"
      tags = {
        Environment = "dev"
      }
    }
    """
    
    result = converter.tf_to_cf(tf_content)
    
    assert "Resources" in result
    assert "example" in result["Resources"]
    assert result["Resources"]["example"]["Type"] == "AWS::S3::Bucket"
    assert result["Resources"]["example"]["Properties"]["BucketName"] == "my-test-bucket"

def test_cf_to_tf_basic_s3():
    converter = CloudFormatConverter()
    cf_content = """
    Resources:
      MyBucket:
        Type: AWS::S3::Bucket
        Properties:
          BucketName: my-test-bucket
          Tags:
            - Key: Environment
              Value: dev
    """
    
    result = converter.cf_to_tf(cf_content)
    assert 'resource "aws_s3_bucket" "MyBucket"' in result
    assert '"bucket" = "my-test-bucket"' in result

def test_variable_conversion():
    converter = CloudFormatConverter()
    tf_content = """
    variable "environment" {
      type        = string
      description = "Environment name"
      default     = "dev"
    }
    """
    
    result = converter.tf_to_cf(tf_content)
    assert "Parameters" in result
    assert "environment" in result["Parameters"]
    assert result["Parameters"]["environment"]["Type"] == "String"
    assert result["Parameters"]["environment"]["Default"] == "dev"

def test_complex_resource_conversion():
    converter = CloudFormatConverter()
    tf_content = """
    resource "aws_lambda_function" "example" {
      filename         = "lambda.zip"
      function_name    = "example_lambda"
      role            = aws_iam_role.lambda_role.arn
      handler         = "index.handler"
      runtime         = "python3.9"
      
      environment {
        variables = {
          ENVIRONMENT = "dev"
        }
      }
      
      depends_on = [aws_iam_role_policy_attachment.lambda_policy]
    }
    """
    
    result = converter.tf_to_cf(tf_content)
    assert "Resources" in result
    assert "example" in result["Resources"]
    assert result["Resources"]["example"]["Type"] == "AWS::Lambda::Function"
    assert "DependsOn" in result["Resources"]["example"]