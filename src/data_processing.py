name: Scheduled Data Processing

on:
  push:
    branches:
      - main
  schedule:
    - cron: '0 0 * * *'  # Runs at 00:00 UTC every day
  workflow_dispatch:     # Manual trigger for testing or on-demand processing

jobs:
  run-data-processing:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Set up Python 3.12
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

    - name: Run data processing script
      run: |
        set -e
        python src/data_processing.py

    - name: Commit and push the processed data
      if: success()
      run: |
        git config --global user.name "GitHub Actions"
        git config --global user.email "actions@github.com"
        git add data/
        git diff --quiet && git diff --staged --quiet || git commit -m "Update processed data on $(date +'%Y-%m-%d %H:%M:%S')"
        git push
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

    - name: Send Slack notification on success
      if: success()
      uses: 8398a7/action-slack@v3
      with:
        status: success
        text: "Data processing workflow completed successfully!"
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}

    - name: Send Slack notification on failure
      if: failure()
      uses: 8398a7/action-slack@v3
      with:
        status: failure
        text: "Data processing workflow failed. Please check the logs."
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
