output "landing_bucket" {
 value = aws_s3_bucket.landing.bucket
}

output "output_queue_url" {
 value = aws_sqs_queue.out.id
}
