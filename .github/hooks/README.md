# Session Start Security Hook Documentation

## Overview

This hook implements a **critical security policy** that automatically scans Copilot sessions at startup for sensitive information patterns. If sensitive data is detected, the session is immediately terminated and the violation is logged for audit purposes.

## Hook Components

### 1. **Hook Definition** (`session-start-security-check.json`)
Main hook configuration that defines:
- **Trigger**: `SessionStart` (executes when a Copilot session begins)
- **Action**: `block` (denies session continuation if issues found)
- **Script**: `.github/hooks/sensitive-data-detector.sh` (validation logic)
- **Severity**: `critical` (non-negotiable security policy)

### 2. **Detection Script** (`sensitive-data-detector.sh`)
Bash script that scans for sensitive patterns:

#### Pattern Categories Detected:
- **Credentials**
  - API keys (AWS, Azure, generic)
  - Bearer tokens
  - Passwords, secrets
  
- **Payment Cards**
  - Credit/debit card formats
  - CVV/CVC references
  - Card number patterns
  
- **Personal Identification**
  - Aadhaar numbers (12-digit format)
  - Social Security Numbers (SSN)
  - Passport references
  
- **Email Credentials**
  - Gmail, Outlook, generic email passwords

### 3. **Audit Logging** (`~/.copilot/logs/governance/audit.log`)
All security events logged with:
- ISO 8601 timestamp
- Unique session ID
- Event level (INFO, WARN, ERROR)
- Detected pattern types
- User and hostname context

## How It Works

### Session Start Flow
```
User starts Copilot session
    ↓
SessionStart hook triggered
    ↓
sensitive-data-detector.sh runs
    ↓
Scan environment variables for sensitive patterns
    ↓
Check input context for sensitive data
    ↓
IF sensitive data found:
   ├─ Log violation to audit.log
   ├─ Display error message
   └─ Terminate session (exit 1)
ELSE:
   ├─ Log "security check passed"
   └─ Allow session to continue (exit 0)
```

## Configuration

### Enable/Disable Hook
Edit `.github/hooks/copilot-hooks-config.json`:
```json
{
  "hooked": [
    {
      "id": "session-start-security-check",
      "enabled": true,  // Set to false to disable hook
      "trigger": "SessionStart",
      "path": ".github/hooks/session-start-security-check.json"
    }
  ]
}
```

### Customize Patterns
Edit pattern arrays in `session-start-security-check.json`:
```json
"patterns": {
  "credentials": [
    "password\\s*[:=]",
    "apikey\\s*[:=]",
    "YOUR_CUSTOM_PATTERN"
  ]
}
```

### Modify Log Location
Update in both files:
```json
"logPath": "/custom/log/path"
```

## Audit Log Format

Each entry is valid JSON for easy parsing:
```json
{
  "timestamp": "2026-04-12T10:30:45Z",
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "level": "ERROR",
  "message": "Session blocked: Sensitive information detected",
  "details": {
    "type": "security_violation",
    "detectedPatterns": ["credentials", "identifiers"]
  },
  "user": "somnathbanerjee",
  "hostname": "MacBook-Pro.local"
}
```

### Query Audit Logs
```bash
# View all violations
grep '"level": "ERROR"' ~/.copilot/logs/governance/audit.log

# View today's activity
grep "$(date +%Y-%m-%d)" ~/.copilot/logs/governance/audit.log

# Count blocked sessions
grep '"level": "ERROR"' ~/.copilot/logs/governance/audit.log | wc -l

# Parse with jq
cat ~/.copilot/logs/governance/audit.log | jq '.[] | select(.level == "ERROR")'
```

## Security Benefits

✅ **Prevention**: Blocks inadvertent exposure of credentials in sessions  
✅ **Detection**: Captures all security policy violations for forensics  
✅ **Audit Trail**: Comprehensive logging for compliance requirements  
✅ **Session Control**: Immediately terminates compromised sessions  
✅ **Pattern Coverage**: Detects multiple categories of sensitive data  

## Testing the Hook

### Test 1: Valid Session (Should Pass)
```bash
# Start normal session - no sensitive data
copilot
# Expected: Session starts normally, INFO log entry
```

### Test 2: Detect API Key (Should Block)
```bash
# Set an API key in environment
export TEST_API_KEY="sk-1234567890abcdef"
copilot
# Expected: Session blocked, ERROR log entry
```

### Test 3: Detect Credential Pattern (Should Block)
```bash
# Include password reference
export MY_DB_PASSWORD="secretPassword123"
copilot
# Expected: Session blocked, ERROR log entry
```

### Test 4: Review Audit Log
```bash
cat ~/.copilot/logs/governance/audit.log
# Should show blocked sessions with details
```

## Troubleshooting

### Hook Not Triggering
- Verify `copilot-hooks-config.json` has `"enabled": true`
- Check hook path is correct: `.github/hooks/session-start-security-check.json`
- Ensure script is executable: `chmod +x .github/hooks/sensitive-data-detector.sh`

### False Positives
- Review detected patterns in audit log
- Consider adjusting regex patterns for your use cases
- Whitelist specific variable names if needed

### Log Directory Issues
```bash
# Ensure log directory exists with proper permissions
mkdir -p ~/.copilot/logs/governance
chmod 700 ~/.copilot/logs/governance

# Check write permissions
touch ~/.copilot/logs/governance/audit.log
```

### Script Permission Errors
```bash
# Make script executable
chmod +x /path/to/.github/hooks/sensitive-data-detector.sh

# Verify permissions
ls -lh .github/hooks/sensitive-data-detector.sh
```

## Integration with Governance

This hook integrates with your organization's security governance framework:

1. **Compliance**: Meets data protection requirements (PII/PCI scanning)
2. **Audit**: Provides forensic trail for security reviews
3. **Policy Enforcement**: Non-bypassable session-level protection
4. **Monitoring**: Exportable logs for SIEM integration

## Next Steps

### Related Hooks to Consider Creating
1. **PreToolUse Hook**: Validate user doesn't pass sensitive data to tools
2. **FileWrite Hook**: Prevent writing credentials to files
3. **APICall Hook**: Monitor API requests for credential leakage
4. **Cleanup Hook**: Sanitize logs before session end

### Enhancement Ideas
- [ ] Integrate with Azure Security Center for alerts
- [ ] Add ML-based sensitive data detection
- [ ] Create dashboard from audit logs
- [ ] Implement auto-remediation for violations
- [ ] Add Slack notifications for security events

## References

- **Hook Specification**: GitHub Copilot Hook Architecture
- **Security Standards**: OWASP Top 10, CWE-798 (Hardcoded Credentials)
- **Compliance**: PCI DSS, GDPR, SOC 2
- **Pattern Reference**: NIST Guidelines for Credential Detection

---

**Last Updated**: 2026-04-12  
**Audit Log Location**: `~/.copilot/logs/governance/audit.log`  
**Configuration**: `.github/hooks/`
