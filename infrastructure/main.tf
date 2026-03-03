provider "aws" {
 region = var.aws_region
}

resource "aws_s3_bucket" "landing" {
 bucket_prefix = "serverless-csv-landing-"
}

resource "aws_s3_bucket_public_access_block" "landing" {
 bucket                  = aws_s3_bucket.landing.id
 block_public_acls       = true
 block_public_policy     = true
 ignore_public_acls      = true
 restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "landing" {
 bucket = aws_s3_bucket.landing.id
 versioning_configuration {
   status = "Enabled"
 }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "landing" {
 bucket = aws_s3_bucket.landing.id
 rule {
   apply_server_side_encryption_by_default {
     sse_algorithm = "AES256"
   }
 }
}

resource "aws_sqs_queue" "dlq" {
 name                     = "serverless-csv-dlq"
 sqs_managed_sse_enabled   = true
 message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "out" {
 name                       = "serverless-csv-out"
 sqs_managed_sse_enabled    = true
 visibility_timeout_seconds = 60

 redrive_policy = jsonencode({
   deadLetterTargetArn = aws_sqs_queue.dlq.arn
   maxReceiveCount     = 5
 })
}

resource "aws_iam_role" "lambda_role" {
 name = "serverless-csv-lambda-role"
 assume_role_policy = jsonencode({
   Version = "2012-10-17"
   Statement = [{
     Action = "sts:AssumeRole"
     Effect = "Allow"
     Principal = { Service = "lambda.amazonaws.com" }
   }]
 })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
 role      = aws_iam_role.lambda_role.name
 policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_app_policy" {
 name = "serverless-csv-lambda-app-policy"
 role = aws_iam_role.lambda_role.id
 policy = jsonencode({
   Version = "2012-10-17"
   Statement = [
     {
       Effect   = "Allow"
       Action   = ["s3:GetObject", "s3:ListBucket"]
       Resource = [aws_s3_bucket.landing.arn, "${aws_s3_bucket.landing.arn}/*"]
     },
     {
       Effect   = "Allow"
       Action   = ["sqs:SendMessage"]
       Resource = aws_sqs_queue.out.arn
     }
   ]
 })
}

# NOTE:
# In production, Lambda code is packaged by CI/CD and referenced via:
#  - filename/source_code_hash (zip), OR
#  - s3_bucket/s3_key (artifact bucket), OR
#  - image_uri (ECR).
# This public repo focuses on architecture, security and permissions.
resource "aws_lambda_function" "processor" {
 function_name = "serverless-csv-processor"
 role          = aws_iam_role.lambda_role.arn
 runtime       = "python3.11"
 handler       = "csv_pipeline.cli.main"
 timeout       = 60
 memory_size   = 256

 environment {
   variables = {
     OUTPUT_QUEUE_URL = aws_sqs_queue.out.id
     BUCKET_NAME      = aws_s3_bucket.landing.bucket
   }
 }
}

resource "aws_lambda_permission" "allow_s3_invoke" {
 statement_id  = "AllowExecutionFromS3"
 action        = "lambda:InvokeFunction"
 function_name = aws_lambda_function.processor.function_name
 principal     = "s3.amazonaws.com"
 source_arn    = aws_s3_bucket.landing.arn
}

resource "aws_s3_bucket_notification" "landing_notifications" {
 bucket = aws_s3_bucket.landing.id

 lambda_function {
   lambda_function_arn = aws_lambda_function.processor.arn
   events              = ["s3:ObjectCreated:*"]
   filter_suffix       = ".csv"
 }

 depends_on = [aws_lambda_permission.allow_s3_invoke]
}
