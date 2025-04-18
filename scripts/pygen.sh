#!/bin/bash

# Set the JIRA ticket field.
FIELD="description"

# Run with options.
python3 ../pygen.py --field ${FIELD} --log-level info --split --no-test-cases "$@"
