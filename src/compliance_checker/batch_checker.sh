#!/bin/bash
# Batch Python Standards Compliance Checker
# This script checks multiple repositories for compliance in an unattended manner

set -e

# Configuration
GITHUB_ORG="${GITHUB_ORG:-LiveData-Inc}"
OUTPUT_DIR="${OUTPUT_DIR:-compliance-results}"
CHECKER_SCRIPT="${CHECKER_SCRIPT:-check_python_project_standards.py}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."

    # Check for Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed"
        exit 1
    fi

    # Check for gh CLI
    if ! command -v gh &> /dev/null; then
        echo "❌ GitHub CLI (gh) is required but not installed"
        echo "Install with: brew install gh"
        exit 1
    fi

    # Check authentication
    if [ -n "$GITHUB_TOKEN" ] || [ -n "$GH_TOKEN" ]; then
        echo "✅ Using token authentication"
        export USE_TOKEN="--use-token"
    elif gh auth status &> /dev/null; then
        echo "✅ Using gh CLI authentication"
        export USE_TOKEN=""
    else
        echo "❌ No authentication found"
        echo "Either set GITHUB_TOKEN/GH_TOKEN or run: gh auth login"
        exit 1
    fi

    # Check for required Python packages
    python3 -c "import toml" 2>/dev/null || {
        echo "Installing required Python packages..."
        pip install toml
    }
}

# Function to get Python repositories
get_python_repos() {
    echo "Fetching Python repositories from $GITHUB_ORG..."

    if [ -n "$GITHUB_TOKEN" ] || [ -n "$GH_TOKEN" ]; then
        # Use token for API call
        export GH_TOKEN="${GITHUB_TOKEN:-$GH_TOKEN}"
    fi

    # Get repos with Python-related topics
    gh api \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        "/orgs/$GITHUB_ORG/repos?type=all&per_page=100" \
        --jq '.[] | select(.topics[]? | IN("python-lib", "python-stack", "python-app", "python-shared", "composite-app")) | .full_name' \
        2>/dev/null || {
            echo "Failed to fetch repositories. Check your authentication."
            exit 1
        }
}

# Function to check a single repository
check_repo() {
    local repo=$1
    local output_file="$OUTPUT_DIR/${repo//\//_}.txt"

    echo -n "Checking $repo... "

    # Run the compliance checker
    if python3 "$CHECKER_SCRIPT" "$repo" $USE_TOKEN > "$output_file" 2>&1; then
        # Extract score from output
        score=$(grep "Compliance Score:" "$output_file" | sed -E 's/.*Compliance Score: ([0-9.]+)%.*/\1/')

        if [ -z "$score" ]; then
            echo -e "${RED}ERROR${NC}"
            return 1
        elif (( $(echo "$score >= 90" | bc -l) )); then
            echo -e "${GREEN}EXCELLENT ($score%)${NC}"
        elif (( $(echo "$score >= 75" | bc -l) )); then
            echo -e "${YELLOW}GOOD ($score%)${NC}"
        else
            echo -e "${RED}NEEDS WORK ($score%)${NC}"
        fi

        echo "$repo,$score" >> "$OUTPUT_DIR/summary.csv"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

# Function to generate summary report
generate_summary() {
    echo ""
    echo "Generating summary report..."

    local total=$(wc -l < "$OUTPUT_DIR/summary.csv")
    local compliant=$(awk -F, '$2 >= 75' "$OUTPUT_DIR/summary.csv" | wc -l)
    local excellent=$(awk -F, '$2 >= 90' "$OUTPUT_DIR/summary.csv" | wc -l)

    cat > "$OUTPUT_DIR/summary.md" << EOF
# Python Standards Compliance Report

**Date**: $(date '+%Y-%m-%d %H:%M:%S')
**Organization**: $GITHUB_ORG
**Total Repositories**: $total

## Statistics
- **Excellent (≥90%)**: $excellent
- **Compliant (≥75%)**: $compliant
- **Non-Compliant (<75%)**: $((total - compliant))

## Repository Scores

| Repository | Score | Status |
|------------|-------|--------|
EOF

    # Sort by score and add to report
    sort -t, -k2 -rn "$OUTPUT_DIR/summary.csv" | while IFS=, read -r repo score; do
        if (( $(echo "$score >= 90" | bc -l) )); then
            status="🟢 Excellent"
        elif (( $(echo "$score >= 75" | bc -l) )); then
            status="🟡 Good"
        else
            status="🔴 Needs Work"
        fi
        echo "| $repo | ${score}% | $status |" >> "$OUTPUT_DIR/summary.md"
    done

    echo ""
    echo "Summary report saved to: $OUTPUT_DIR/summary.md"
}

# Main execution
main() {
    echo "==================================="
    echo "Python Standards Compliance Checker"
    echo "==================================="
    echo ""

    # Check prerequisites
    check_prerequisites

    # Create output directory
    rm -rf "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"

    # Initialize summary CSV
    echo "Repository,Score" > "$OUTPUT_DIR/summary.csv"

    # Get list of repositories
    repos=$(get_python_repos)

    if [ -z "$repos" ]; then
        echo "No Python repositories found in $GITHUB_ORG"
        exit 1
    fi

    repo_count=$(echo "$repos" | wc -l)
    echo "Found $repo_count Python repositories"
    echo ""

    # Check each repository
    failed_count=0
    while IFS= read -r repo; do
        if ! check_repo "$repo"; then
            ((failed_count++))
        fi
    done <<< "$repos"

    # Generate summary
    generate_summary

    echo ""
    echo "==================================="
    echo "Compliance check complete!"
    echo "Results saved to: $OUTPUT_DIR/"
    echo "==================================="

    # Exit with error if any repos failed
    if [ $failed_count -gt 0 ]; then
        echo "⚠️  $failed_count repositories failed to check"
        exit 1
    fi
}

# Run the main function
main "$@"