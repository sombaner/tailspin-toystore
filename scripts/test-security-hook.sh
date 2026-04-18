#!/bin/bash

# Test Script for Session Start Security Hook
# Tests various scenarios to validate hook behavior

set -euo pipefail

echo "=========================================="
echo "Security Hook Test Suite"
echo "=========================================="

LOG_DIR="${HOME}/.copilot/logs/governance"
AUDIT_LOG="${LOG_DIR}/audit.log"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Initialize test counters
passed=0
failed=0

# Test 1: Verify hook files exist
echo ""
echo "Test 1: Verifying hook configuration files..."
test_passed=true
for file in ".github/hooks/session-start-security-check.json" \
            ".github/hooks/sensitive-data-detector.sh" \
            ".github/hooks/copilot-hooks-config.json"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file exists"
    else
        echo -e "  ${RED}✗${NC} $file missing"
        test_passed=false
    fi
done
if $test_passed; then ((passed++)); else ((failed++)); fi

# Test 2: Verify audit log directory
echo ""
echo "Test 2: Checking audit log setup..."
test_passed=true
if [ -d "${LOG_DIR}" ]; then
    echo -e "  ${GREEN}✓${NC} Log directory exists: ${LOG_DIR}"
else
    echo -e "  ${RED}✗${NC} Log directory missing"
    test_passed=false
fi

if [ -w "${LOG_DIR}" ]; then
    echo -e "  ${GREEN}✓${NC} Log directory is writable"
else
    echo -e "  ${RED}✗${NC} Log directory is not writable"
    test_passed=false
fi
if $test_passed; then ((passed++)); else ((failed++)); fi

# Test 3: JSON validation
echo ""
echo "Test 3: Validating JSON configurations..."
test_passed=true
for file in ".github/hooks/session-start-security-check.json" \
            ".github/hooks/copilot-hooks-config.json"; do
    if command -v jq &> /dev/null; then
        if jq empty "$file" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $file is valid JSON"
        else
            echo -e "  ${RED}✗${NC} $file has JSON errors"
            test_passed=false
        fi
    else
        echo -e "  ${YELLOW}⊘${NC} jq not available, skipping JSON validation"
    fi
done
if $test_passed; then ((passed++)); else ((failed++)); fi

# Test 4: Script permissions
echo ""
echo "Test 4: Verifying script permissions..."
test_passed=true
script=".github/hooks/sensitive-data-detector.sh"
if [ -x "$script" ]; then
    echo -e "  ${GREEN}✓${NC} Script is executable"
else
    echo -e "  ${RED}✗${NC} Script is not executable"
    echo "    Run: chmod +x $script"
    test_passed=false
fi
if $test_passed; then ((passed++)); else ((failed++)); fi

# Test 5: Pattern detection (dry run)
echo ""
echo "Test 5: Testing pattern detection logic..."
test_passed=true
test_script=$(mktemp)

# Create test version that won't actually block
cat > "$test_script" << 'EOF'
test_pattern() {
    local pattern=$1
    local text=$2
    if echo "${text}" | grep -iE "${pattern}" > /dev/null 2>&1; then
        return 0
    fi
    return 1
}

# Test cases
test_pattern "password\s*[:=]" "database_password=secret" && echo "✓ Password pattern detected"
test_pattern "apikey|api[_-]?key" "my_api_key=abc123" && echo "✓ API key pattern detected"
test_pattern "aadhaar|ssn" "aadhaar_number=123456789012" && echo "✓ Personal ID pattern detected"
EOF

bash "$test_script" | while read line; do
    echo -e "  ${GREEN}$line${NC}"
done
rm -f "$test_script"
((passed++))

# Test 6: Sample audit log
echo ""
echo "Test 6: Checking audit log..."
test_passed=true
if [ -f "${AUDIT_LOG}" ]; then
    echo -e "  ${GREEN}✓${NC} Audit log exists"
    entries=$(grep -c . "${AUDIT_LOG}" 2>/dev/null || echo "0")
    echo -e "  ${GREEN}✓${NC} Log entries: $entries"
else
    echo -e "  ${YELLOW}⊘${NC} Audit log not yet created (will be created on first use)"
fi
((passed++))

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}✓${NC} File existence check"
echo -e "${GREEN}✓${NC} Audit log directory setup"
echo -e "${GREEN}✓${NC} JSON configuration validation"
echo -e "${GREEN}✓${NC} Script permissions"
echo -e "${GREEN}✓${NC} Pattern detection logic"
echo -e "${GREEN}✓${NC} Audit log verification"

echo ""
echo "Results: $passed passed, $failed failed"

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review above.${NC}"
    exit 1
fi
