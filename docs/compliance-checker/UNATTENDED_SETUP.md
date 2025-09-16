# Unattended Python Standards Compliance Checking

This guide explains how to set up automated, unattended compliance checking for Python repositories.

## Authentication Methods

### Option 1: GitHub Actions (Recommended for Nightly Checks)

The `.github/workflows/nightly-compliance-check.yml` workflow runs automatically:

- **Schedule**: 2 AM UTC daily
- **Authentication**: Built-in `GITHUB_TOKEN`
- **Output**: Creates GitHub issues with results
- **No setup required** - just commit the workflow file

To enable:
```bash
# Commit the workflow to your repository
git add .github/workflows/nightly-compliance-check.yml
git commit -m "Add nightly compliance checks"
git push
```

### Option 2: Personal Access Token (For External Systems)

1. **Create a GitHub Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token with scopes:
     - `repo` (full control of private repositories)
     - `read:org` (read organization data)
   - Save the token securely

2. **Set up the token**:
   ```bash
   # For one-time use
   export GITHUB_TOKEN=ghp_your_token_here

   # For persistent use (add to ~/.bashrc or ~/.zshrc)
   echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.bashrc

   # For CI/CD systems, add as a secret
   ```

3. **Run the checker**:
   ```bash
   # Single repository
   python src/compliance_checker/check_python_project_standards.py LiveData-Inc/repo-name --auth=token

   # Batch check all Python repos
   ./src/compliance_checker/batch_checker.sh
   ```

### Option 3: GitHub App (For Enterprise Scale)

For organizations needing fine-grained permissions:

1. **Create a GitHub App**:
   - Go to Organization Settings → Developer settings → GitHub Apps
   - Create new GitHub App with permissions:
     - Repository contents: Read
     - Repository metadata: Read
     - Organization members: Read

2. **Install the App**:
   - Install on your organization
   - Note the Installation ID

3. **Generate App Token** (expires after 1 hour):
   ```bash
   # Using gh CLI with app authentication
   gh auth login --with-token < app-token.txt
   ```

## Automated Execution Options

### 1. Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add nightly check at 2 AM
0 2 * * * cd /path/to/checker && ./src/compliance_checker/batch_checker.sh >> /var/log/compliance.log 2>&1

# With email notification
0 2 * * * cd /path/to/checker && ./src/compliance_checker/batch_checker.sh | mail -s "Compliance Report" team@company.com
```

### 2. systemd Timer (Linux)

Create `/etc/systemd/system/python-compliance.service`:
```ini
[Unit]
Description=Python Standards Compliance Check
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=compliance
Environment="GITHUB_TOKEN=ghp_your_token_here"
Environment="GITHUB_ORG=LiveData-Inc"
WorkingDirectory=/opt/compliance-checker
ExecStart=/opt/compliance-checker/src/compliance_checker/batch_checker.sh
StandardOutput=journal
StandardError=journal
```

Create `/etc/systemd/system/python-compliance.timer`:
```ini
[Unit]
Description=Run Python compliance check daily
Requires=python-compliance.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

Enable the timer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable python-compliance.timer
sudo systemctl start python-compliance.timer
```

### 3. Jenkins Pipeline

```groovy
pipeline {
    agent any

    triggers {
        cron('0 2 * * *')  // 2 AM daily
    }

    environment {
        GITHUB_TOKEN = credentials('github-token')
        GITHUB_ORG = 'LiveData-Inc'
    }

    stages {
        stage('Check Compliance') {
            steps {
                sh '''
                    python3 -m pip install toml
                    ./src/compliance_checker/batch_checker.sh
                '''
            }
        }

        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'compliance-results/**/*'
                publishHTML target: [
                    reportDir: 'compliance-results',
                    reportFiles: 'summary.md',
                    reportName: 'Compliance Report'
                ]
            }
        }

        stage('Notify') {
            when {
                expression { currentBuild.result == 'FAILURE' }
            }
            steps {
                emailext (
                    subject: "Compliance Check Failed",
                    body: "Some repositories are non-compliant. Check the report.",
                    to: 'team@company.com'
                )
            }
        }
    }
}
```

### 4. AWS Lambda

For serverless execution:

```python
import os
import boto3
import subprocess
from datetime import datetime

def lambda_handler(event, context):
    # Set up authentication
    os.environ['GITHUB_TOKEN'] = boto3.client('secretsmanager').get_secret_value(
        SecretId='github-token'
    )['SecretString']

    # Run compliance check
    result = subprocess.run(
        ['python3', 'src/compliance_checker/check_python_project_standards.py', 'LiveData-Inc/repo', '--auth=token'],
        capture_output=True,
        text=True
    )

    # Store results in S3
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket='compliance-reports',
        Key=f"reports/{datetime.now().isoformat()}.txt",
        Body=result.stdout
    )

    return {
        'statusCode': 200 if result.returncode == 0 else 500,
        'body': result.stdout
    }
```

## Monitoring and Alerting

### Slack Integration

Add to `src/compliance_checker/batch_checker.sh`:
```bash
send_slack_notification() {
    local webhook_url="$SLACK_WEBHOOK_URL"
    local message="$1"

    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\"$message\"}" \
        "$webhook_url"
}

# After generating summary
if [ $compliant -lt $total ]; then
    send_slack_notification "⚠️ Python Compliance Alert: $((total - compliant)) repositories are non-compliant"
fi
```

### Email Reports

```bash
# Send HTML email with results
cat compliance-results/summary.md | \
    pandoc -f markdown -t html | \
    mail -a "Content-Type: text/html" \
         -s "Python Compliance Report $(date +%Y-%m-%d)" \
         team@company.com
```

## Security Best Practices

1. **Token Storage**:
   - Never commit tokens to version control
   - Use secret management systems (AWS Secrets Manager, HashiCorp Vault)
   - Rotate tokens regularly

2. **Least Privilege**:
   - Create tokens with minimum required permissions
   - Use read-only access where possible

3. **Audit Logging**:
   - Log all compliance check runs
   - Monitor for unauthorized access

4. **Network Security**:
   - Run checks from secure, controlled environments
   - Use VPN/private networks for sensitive repositories

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   ```bash
   # Test authentication
   gh auth status

   # Test token
   curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
   ```

2. **Rate Limiting**:
   - Authenticated requests: 5,000/hour
   - Unauthenticated: 60/hour
   - Solution: Use authentication or implement rate limiting

3. **Network Issues**:
   ```bash
   # Test GitHub API access
   curl -I https://api.github.com

   # Test with proxy if needed
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

## Performance Optimization

For large organizations:

1. **Parallel Processing**:
   ```bash
   # Check repos in parallel (max 5 at a time)
   echo "$repos" | xargs -P 5 -I {} bash -c 'check_repo "{}"'
   ```

2. **Caching**:
   - Cache repository metadata
   - Skip unchanged repositories

3. **Incremental Checks**:
   - Only check repos modified since last run
   - Use GitHub webhooks for event-driven checks

## Reporting Dashboard

Consider using:
- **Grafana**: For visualization
- **Elasticsearch**: For historical data
- **GitHub Pages**: For static reports
- **Power BI/Tableau**: For enterprise reporting

## Support

For issues or questions:
1. Check the logs in `compliance-results/`
2. Verify authentication with `gh auth status`
3. Test individual repos with verbose output
4. Review GitHub API status: https://www.githubstatus.com/