#!/bin/bash

# Automated Deployment Testing Script

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

echo "🧪 TESTING DEPLOYMENT"
echo "===================="
echo ""

# Get deployment URL
if [ -f ".deployment-info" ]; then
    source .deployment-info
    print_info "Using deployment URL: $DEPLOYMENT_URL"
else
    read -p "Enter your Vercel deployment URL (without https://): " DEPLOYMENT_URL
    if [[ ! $DEPLOYMENT_URL =~ ^https:// ]]; then
        DEPLOYMENT_URL="https://$DEPLOYMENT_URL"
    fi
fi

# Test 1: Health endpoint
print_test "Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$DEPLOYMENT_URL/api/health")
HEALTH_CODE=$(echo "$HEALTH_RESPONSE" | tail -1)
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | sed '$d')

if [ "$HEALTH_CODE" = "200" ]; then
    print_pass "Health endpoint returns 200 OK"
    echo "Response: $HEALTH_BODY"
else
    print_fail "Health endpoint failed (HTTP $HEALTH_CODE)"
    echo "Response: $HEALTH_BODY"
fi

echo ""

# Test 2: Auth info endpoint
print_test "Testing auth info endpoint..."
AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$DEPLOYMENT_URL/api/auth/")
AUTH_CODE=$(echo "$AUTH_RESPONSE" | tail -1)
AUTH_BODY=$(echo "$AUTH_RESPONSE" | sed '$d')

if [ "$AUTH_CODE" = "200" ]; then
    print_pass "Auth info endpoint returns 200 OK"
    echo "Response: $AUTH_BODY"
else
    print_fail "Auth info endpoint failed (HTTP $AUTH_CODE)"
    echo "Response: $AUTH_BODY"
fi

echo ""

# Test 3: Login with correct credentials
print_test "Testing login with correct credentials..."
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=admin@entrepedia.ai&password=admin123" \
    "$DEPLOYMENT_URL/api/auth/login")

LOGIN_CODE=$(echo "$LOGIN_RESPONSE" | tail -1)
LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

if [ "$LOGIN_CODE" = "200" ]; then
    print_pass "Login with correct credentials successful"
    # Extract token
    TOKEN=$(echo "$LOGIN_BODY" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
    if [ ! -z "$TOKEN" ]; then
        print_pass "JWT token received: ${TOKEN:0:20}..."
    else
        print_fail "No JWT token in response"
    fi
else
    print_fail "Login failed (HTTP $LOGIN_CODE)"
    echo "Response: $LOGIN_BODY"
fi

echo ""

# Test 4: Login with wrong credentials
print_test "Testing login with wrong credentials..."
WRONG_LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=wrong@example.com&password=wrongpass" \
    "$DEPLOYMENT_URL/api/auth/login")

WRONG_CODE=$(echo "$WRONG_LOGIN_RESPONSE" | tail -1)

if [ "$WRONG_CODE" = "401" ]; then
    print_pass "Wrong credentials correctly rejected (401)"
else
    print_fail "Wrong credentials should return 401, got $WRONG_CODE"
fi

echo ""

# Test 5: CORS check
print_test "Testing CORS headers..."
CORS_RESPONSE=$(curl -s -I \
    -H "Origin: https://localhost:3000" \
    -H "Access-Control-Request-Method: POST" \
    -H "Access-Control-Request-Headers: Content-Type" \
    -X OPTIONS \
    "$DEPLOYMENT_URL/api/auth/login")

if echo "$CORS_RESPONSE" | grep -q "access-control-allow-origin"; then
    print_pass "CORS headers present"
else
    print_fail "CORS headers missing"
fi

echo ""
echo "📊 TEST SUMMARY"
echo "==============="

# Count results
TOTAL_TESTS=5
PASSED=0

# Re-run quick checks for summary
[ "$HEALTH_CODE" = "200" ] && ((PASSED++))
[ "$AUTH_CODE" = "200" ] && ((PASSED++))
[ "$LOGIN_CODE" = "200" ] && ((PASSED++))
[ "$WRONG_CODE" = "401" ] && ((PASSED++))
echo "$CORS_RESPONSE" | grep -q "access-control-allow-origin" && ((PASSED++))

echo "Tests passed: $PASSED/$TOTAL_TESTS"

if [ $PASSED -eq $TOTAL_TESTS ]; then
    echo ""
    print_pass "🎉 ALL TESTS PASSED! Deployment is working correctly."
    echo ""
    echo "✅ Your deployment is ready:"
    echo "   URL: $DEPLOYMENT_URL"
    echo "   Login: admin@entrepedia.ai / admin123"
    echo ""
    echo "Next step: Update your frontend to use this API URL"
else
    echo ""
    print_fail "⚠️ Some tests failed. Check the logs above."
    echo ""
    echo "🔧 Troubleshooting:"
    echo "1. Check Vercel function logs in dashboard"
    echo "2. Verify deployment completed successfully"
    echo "3. Wait a few minutes and try again (functions need time to start)"
fi