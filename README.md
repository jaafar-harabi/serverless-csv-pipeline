# Serverless CSV Processing Pipeline (AWS)

A production-oriented reference implementation of a serverless batch ingestion pipeline:
**S3 → Lambda → SQS**.

It parses four related CSV datasets (`clients`, `portfolios`, `accounts`, `transactions`), performs deterministic aggregation, and emits JSON messages.

> In this repo, queue publishing is represented by **JSON Lines printed to stdout** to keep the project runnable without AWS.

## Message Types

### `client_message`
- one per client
- `taxes_paid` is the sum of taxes across all accounts owned by the client

### `portfolio_message`
- one per portfolio
- `sum_of_deposits` is the sum of amounts where `keyword == "DEPOSIT"`

### `error_message`
- emitted for malformed inputs or missing references
- processing continues (fail-soft behavior)

## Run locally

```bash
pip install -e ".[dev]"
python -m csv_pipeline.cli clients.csv portfolios.csv accounts.csv transactions.csv
