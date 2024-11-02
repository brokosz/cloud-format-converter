variable "environment" {
  type        = string
  description = "Environment name"
  default     = "dev"
}

variable "bucket_prefix" {
  type        = string
  description = "Prefix for bucket names"
  default     = "my-company"
}

resource "aws_s3_bucket" "storage" {
  bucket = "${var.bucket_prefix}-${var.environment}-storage"
  
  tags = {
    Environment = var.environment
    Managed     = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "storage_versioning" {
  bucket = aws_s3_bucket.storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_dynamodb_table" "lock_table" {
  name           = "${var.bucket_prefix}-${var.environment}-lock"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "LockID"
  
  attribute {
    name = "LockID"
    type = "S"
  }
  
  tags = {
    Environment = var.environment
    Managed     = "terraform"
  }
}

output "bucket_name" {
  value       = aws_s3_bucket.storage.bucket
  description = "Name of the created S3 bucket"
}

output "table_name" {
  value       = aws_dynamodb_table.lock_table.name
  description = "Name of the created DynamoDB table"
}