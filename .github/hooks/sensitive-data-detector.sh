#!/bin/bash

# Sensitive Data Detection Script for Copilot Session Start Hook
# This script validates context for sensitive information patterns and blocks if found

set -euo pipefail

# Configuration
LOG_DIR="${HOME}/.copilot/logs/governance"
AUDIT_LOG="${LOG_DIR}/audit.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SESSION_ID="${COPILOT_SESSION_ID:-$(uuidgen 2>/dev/null || echo 'unknown')}"

# Ensure log directory exists
mkdir -p "${LOG_DIR}"

# Color codes for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to log audit entries
log_audit() {
    local level=$1
    local message=$2
    local details=$3
    
    echo "{
  \"timestamp\": \"${TIMESTAMP}\",
  \"sessionId\": \"${SESSION_ID}\",
  \"level\": \"${level}\",
  \"message\": \"${message}\",
  \"details\": ${details},
  \"user\": \"$(whoami)\",
  \"hostname\": \"$(hostname)\"
}" >> "${AUDIT_LOG}"
}

# Function to check for sensitive patterns
check_sensitive_patterns() {
    local input=$1
    local found_issues=false
    local issues_json="[]"
    
    # Credentials patterns
    if echo "${input}" | grep -iE "password\s*[:=]|apikey|api[_-]?key|Bearer\s+[A-Za-z0-9]|AKIA[0-9A-Z]{16}|AWS[A-Za-z0-9/+=]{40}" > /dev/null 2>&1; then
        found_issues=true
        issues_json=$(echo "$issues_json" | jq '. += [{"type": "credentials", "pattern": "api_key, password, or bearer token"}]')
    fi
    
    # Payment card patterns (basic)
    if echo "${input}" | grep -iE "card[_-]?number|cvv|cvc|visa|mastercard|amex|diners" > /dev/null 2>&1; then
        found_issues=true
        issues_json=$(echo "$issues_json" | jq '. += [{"type": "payment_card", "pattern": "credit/debit card reference"}]')
    fi
    
    # Personal identification patterns
    if echo "${input}" | grep -iE "aadhaar|ssn|social\s*security|passport" > /dev/null 2>&1; then
        found_issues=true
        issues_json=$(echo "$issues_json" | jq '. += [{"type": "personal_identification", "pattern": "aadhaar, SSN, or passport reference"}]')
    fi
    
    # Email password patterns
    if echo "${input}" | grep -iE "(gmail|outlook|email).*password" > /dev/null 2>&1; then
        found_issues=true
        issues_json=$(echo "$issues_json" | jq '. += [{"type": "email_password", "pattern": "email account credentials"}]')
    fi
    
    if [ "$found_issues" = true ]; then
        return 1
    fi
    return 0
}

# Main execution
echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] Initiating security scan for session start...${NC}"

# Gather context data to check
CONTEXT_DATA=""

# Check environment for sensitive patterns (excluding standard vars)
SENSITIVE_ENV_VARS=("PASSWORD" "SECRET" "TOKEN" "KEY" "CREDENTIAL" "AWS_SECRET" "AZURE_" "GITHUB_TOKEN")
for var in "${SENSITIVE_ENV_VARS[@]}"; do
    if env | grep -i "^${var}" > /dev/null 2>&1; then
        CONTEXT_DATA+="$(env | grep -i "^${var}" | head -1)"$'\n'
    fi
done

# Check for sensitive patterns in context
if [ -n "${CONTEXT_DATA}" ]; then
    if ! check_sensitive_patterns "${CONTEXT_DATA}"; then
        echo -e "${RED}[ERROR] Sensitive information detected in session context!${NC}"
        
        log_audit "ERROR" "Session blocked: Sensitive information detected" \
            "{\"type\": \"security_violation\", \"detectedPatterns\": [\"credentials\", \"identifiers\", \"payment_info\"]}"
        
        echo -e "${RED}[BLOCKED] This session has been terminated due to security policy.${NC}"
        echo -e "${RED}[INFO] Audit log: ${AUDIT_LOG}${NC}"
        echo -e "${RED}[ACTION] Please review sensitive data handling policies before retrying.${NC}"
        
        exit 1
    fi
fi

# Log successful security check
log_audit "INFO" "Security scan passed: No sensitive information detected" \
    "{\"type\": \"security_check_passed\", \"contextScanned\": true}"

echo -e "${GREEN}[SUCCESS] Security scan passed. Session initialization allowed.${NC}"
exit 0
