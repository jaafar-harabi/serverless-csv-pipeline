# Design Decisions

## Deterministic Output
Messages are emitted in sorted reference order to keep results stable and testable.

## Strict Deposit Classification
Deposits are defined by keyword == "DEPOSIT" to avoid misclassifying other positive amounts.

## Fail-soft Error Handling
Malformed rows and missing references produce error_message objects; processing continues.

## Lambda Packaging Note
Terraform in this repo focuses on resources, security, and wiring. In production, code is packaged by CI/CD and referenced via zip/S3/ECR.
