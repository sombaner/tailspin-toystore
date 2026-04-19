#!/bin/bash

# Setup Script for Session Start Security Hook
# Installs and configures the sensitive data detection hook for Copilot

set -euo pipefail

echo "=========================================="
echo "Copilot Session Security Hook Setup"
echo "=========================================="

HOOK_DIR=".github/hooks"
LOG_DIR="${HOME}/.copilot/logs/governance"
AUDIT_LOG="${LOG_DIR}/audit.log"

# Step 1: Create log directory
echo "[1/5] Creating audit log directory..."
mkdir -p "${LOG_DIR}"
chmod 700 "${LOG_DIR}"
echo "✓ Created: ${LOG_DIR}"

# Step 2: Verify hook files exist
echo "[2/5] Verifying hook configuration files..."
REQUIRED_FILES=(
    "${HOOK_DIR}/session-start-security-check.json"
    "${HOOK_DIR}/sensitive-data-detector.sh"
    "${HOOK_DIR}/copilot-hooks-config.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ Found: $file"
    else
        echo "✗ MISSING: $file"
        exit 1
    fi
done

# Step 3: Set proper permissions
echo "[3/5] Setting file permissions..."
chmod 755 "${HOOK_DIR}/sensitive-data-detector.sh"
chmod 644 "${HOOK_DIR}/session-start-security-check.json"
chmod 644 "${HOOK_DIR}/copilot-hooks-config.json"
echo "✓ Permissions set correctly"

# Step 4: Initialize audit log
echo "[4/5] Initializing audit log..."
touch "${AUDIT_LOG}"
chmod 600 "${AUDIT_LOG}"
cat > "${AUDIT_LOG}" << EOF
{
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "event": "audit_log_initialized",
  "version": "1.0",
  "config": {
    "logPath": "${LOG_DIR}",
    "logFile": "audit.log"
  }
}
EOF
echo "✓ Audit log initialized: ${AUDIT_LOG}"

# Step 5: Verify setup
echo "[5/5] Verifying setup..."
echo ""
echo "Configuration Summary:"
echo "  • Hook ID: session-start-security-check"
echo "  • Trigger: SessionStart"
echo "  • Action: Block and log"
echo "  • Status: ENABLED"
echo "  • Audit Log: ${AUDIT_LOG}"
echo ""

# Display next steps
echo "=========================================="
echo "✓ Setup Complete!"
echo "=========================================="
echo ""
echo "Next Steps:"
echo "  1. Review hook patterns in: ${HOOK_DIR}/session-start-security-check.json"
echo "  2. Test the hook with: ./scripts/test-security-hook.sh"
echo "  3. Monitor logs: tail -f ${AUDIT_LOG}"
echo "  4. See README.md for detailed documentation"
echo ""
echo "To disable hook (if needed):"
echo "  Edit: ${HOOK_DIR}/copilot-hooks-config.json"
echo "  Set: \"enabled\": false"
echo ""
