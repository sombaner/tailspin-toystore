# Copilot Session Security Hook - Quick Reference

## 📋 What This Hook Does

Automatically detects and **blocks Copilot sessions** that contain sensitive information patterns:
- ✗ Passwords, API keys, Bearer tokens  
- ✗ Credit/debit card data  
- ✗ Personal IDs (Aadhaar, SSN, passport)  
- ✗ Email account credentials  

All violations logged to: `~/.copilot/logs/governance/audit.log`

---

## 🚀 Quick Start

### 1. Run Setup
```bash
bash .github/hooks/setup.sh
```

### 2. Run Tests  
```bash
bash scripts/test-security-hook.sh
```

### 3. Monitor Logs
```bash
tail -f ~/.copilot/logs/governance/audit.log
```

---

## 📁 Hook Files

| File | Purpose |
|------|---------|
| `session-start-security-check.json` | Hook definition & patterns |
| `sensitive-data-detector.sh` | Detection script |
| `copilot-hooks-config.json` | Hook registration config |
| `README.md` | Full documentation |
| `setup.sh` | Installation script |

Root Directory: `.github/hooks/`

---

## 🔍 Pattern Detection

### Credentials (Enabled)
```
- password=, apikey=, api_key=
- Bearer tokens
- AWS_SECRET_*, AWS AKIA format
- Generic secret/token patterns
```

### Payment Cards (Enabled)
```
- card_number=, cvv=, cvc=
- Visa, Mastercard, Amex references
- 13-19 digit card patterns
```

### Personal IDs (Enabled)
```
- aadhaar= (12 digits)
- ssn= (social security)
- passport= references
```

### Email Credentials (Enabled)
```
- gmail.password=
- outlook.password=
- email.*password= patterns
```

---

## 📊 Audit Log Format

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

---

## 🛠️ Common Operations

### View All Violations
```bash
grep '"level": "ERROR"' ~/.copilot/logs/governance/audit.log
```

### View Today's Activity
```bash
grep "$(date +%Y-%m-%d)" ~/.copilot/logs/governance/audit.log
```

### Count Blocked Sessions
```bash
grep '"level": "ERROR"' ~/.copilot/logs/governance/audit.log | wc -l
```

### Parse with jq
```bash
cat ~/.copilot/logs/governance/audit.log | jq '.[] | select(.level == "ERROR")'
```

### Enable/Disable Hook
```bash
# Edit and set "enabled" field
nano .github/hooks/copilot-hooks-config.json
```

---

## ⚙️ Configuration

### Modify Patterns
Edit: `.github/hooks/session-start-security-check.json`

```json
"patterns": {
  "credentials": [
    "password\\s*[:=]",
    "your_custom_pattern_here"
  ]
}
```

### Change Log Location
Edit both files:
```json
"logPath": "/your/custom/path"
```

### Adjust Log Retention
Create a cron job:
```bash
# Delete logs older than 90 days
find ~/.copilot/logs/governance -name "*.log" -mtime +90 -delete
```

---

## 🧪 Testing

### Test: Verify Configuration
```bash
bash scripts/test-security-hook.sh
```

### Test: Pattern Detection (Manual)
```bash
# This should trigger detection (in isolated test env)
export TEST_API_KEY="sk_test_1234567890"
# Session would block if hook is active
```

### Test: Audit Log Creation
```bash
# Check log exists and has proper format
cat ~/.copilot/logs/governance/audit.log | jq
```

---

## 🔐 Security Benefits

| Benefit | Details |
|---------|---------|
| **Prevention** | Blocks accidental credential exposure in sessions |
| **Detection** | Captures all policy violations for forensics |
| **Audit Trail** | Comprehensive JSON logs for compliance |
| **Non-bypassable** | Session-level enforcement (enforced before agent runs) |
| **Pattern Coverage** | Detects multiple sensitive data categories |

---

## 📖 Documentation

- **Full Guide**: `.github/hooks/README.md`
- **This File**: `.github/hooks/QUICKREF.md`
- **Setup Script**: `.github/hooks/setup.sh`
- **Test Script**: `scripts/test-security-hook.sh`

---

## ❓ Troubleshooting

| Issue | Solution |
|-------|----------|
| Hook not triggering | Check `enabled: true` in `copilot-hooks-config.json` |
| Permission errors | Run: `chmod +x .github/hooks/sensitive-data-detector.sh` |
| Log not created | Verify: `mkdir -p ~/.copilot/logs/governance && chmod 700` |
| False positives | Review patterns in `session-start-security-check.json` |
| jq errors | Install jq: `brew install jq` (macOS) or `apt-get install jq` (Linux) |

---

## 📞 Support

- **Logs**: `~/.copilot/logs/governance/audit.log`
- **Config**: `.github/hooks/` directory  
- **Tests**: `bash scripts/test-security-hook.sh`
- **Docs**: See `.github/hooks/README.md` for comprehensive guide

---

**Last Updated**: 2026-04-12  
**Hook Version**: 1.0  
**Status**: ✅ Production Ready
