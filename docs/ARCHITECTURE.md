# Architecture

## Overview
This project implements a serverless batch ingestion pipeline:
S3 (landing) → Lambda (processor) → SQS (output + DLQ).

## Why S3
- Durable object storage for daily batch files
- Native event notifications
- Simple, auditable ingestion layer

## Why Lambda
- Stateless compute
- Autoscaling and cost efficiency
- Easy to operate with CloudWatch logs/metrics

## Why SQS (+ DLQ)
- Decouples producer from consumers
- Buffers backpressure
- DLQ isolates poison messages and supports operational workflows

## Production Enhancements
- Step Functions or DynamoDB coordination to ensure all required files exist for a given date
- Idempotency markers keyed by <date> to avoid duplicate processing
- Observability: structured logs, metrics, alarms on DLQ depth, tracing
