#!/bin/bash
#
# Test script for Via Node Topology REST API
# 
# Usage: ./test_topology_api.sh [BASE_URL]
# Default BASE_URL: http://localhost:8000
#

set -e

BASE_URL="${1:-http://localhost:8000}"
API_VERSION="v1"
API_BASE="${BASE_URL}/api/${API_VERSION}"

# Authentication credentials (default from application.properties)
USERNAME="${VIA_NODE_USER:-admin}"
PASSWORD="${VIA_NODE_PASSWORD:-password}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "Via Node Topology API Test Suite"
echo "========================================="
echo "Base URL: ${BASE_URL}"
echo "API Base: ${API_BASE}"
echo "Username: ${USERNAME}"
echo ""

# Test 1: Create a host
echo -e "${YELLOW}Test 1: Create Host${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X POST "${API_BASE}/hosts" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "192.168.1.100",
    "hostname": "test-server.example.com",
    "os_type": "Linux",
    "metadata": {"environment": "test", "datacenter": "dc1"}
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
LOCATION=$(echo "$RESPONSE" | grep -i "location:" | awk '{print $2}' || echo "")

if [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✓ Host created successfully (HTTP 201)${NC}"
    echo "  Location: ${LOCATION}"
else
    echo -e "${RED}✗ Failed to create host (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 2: Get the created host
echo -e "${YELLOW}Test 2: Get Host by IP${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X GET "${API_BASE}/hosts/192.168.1.100")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Host retrieved successfully (HTTP 200)${NC}"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ Failed to retrieve host (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 3: Create a domain-port edge
echo -e "${YELLOW}Test 3: Create Domain-Port Edge${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X POST "${API_BASE}/edges/domain-port" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "example.com",
    "port_number": 443,
    "protocol": "TCP"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✓ Domain-port edge created successfully (HTTP 201)${NC}"
else
    echo -e "${RED}✗ Failed to create domain-port edge (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 4: Create a DNS-resolves-to-host edge
echo -e "${YELLOW}Test 4: Create DNS-Resolves-to-Host Edge${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X POST "${API_BASE}/edges/dns-resolves-to-host" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "example.com",
    "ip_address": "192.168.1.100"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "201" ]; then
    echo -e "${GREEN}✓ DNS-resolves-to-host edge created successfully (HTTP 201)${NC}"
else
    echo -e "${RED}✗ Failed to create DNS-resolves-to-host edge (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 5: Get port
echo -e "${YELLOW}Test 5: Get Port${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X GET "${API_BASE}/ports/443/TCP")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Port retrieved successfully (HTTP 200)${NC}"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "${YELLOW}⚠ Port not found (HTTP 404) - This is expected if not created yet${NC}"
else
    echo -e "${RED}✗ Failed to retrieve port (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 6: Get DNS record
echo -e "${YELLOW}Test 6: Get DNS Record${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X GET "${API_BASE}/dns-records/example.com")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ DNS record retrieved successfully (HTTP 200)${NC}"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "${YELLOW}⚠ DNS record not found (HTTP 404) - This is expected if not created yet${NC}"
else
    echo -e "${RED}✗ Failed to retrieve DNS record (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 7: Get non-existent host (should return 404)
echo -e "${YELLOW}Test 7: Get Non-Existent Host (should return 404)${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X GET "${API_BASE}/hosts/10.0.0.1")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "404" ]; then
    echo -e "${GREEN}✓ Correctly returned 404 for non-existent host${NC}"
else
    echo -e "${RED}✗ Expected 404, got HTTP ${HTTP_CODE}${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 8: Create host with invalid IP (should return 400)
echo -e "${YELLOW}Test 8: Create Host with Invalid IP (should return 400)${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X POST "${API_BASE}/hosts" \
  -H "Content-Type: application/json" \
  -d '{
    "ip_address": "invalid-ip",
    "hostname": "test.example.com",
    "os_type": "Linux"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "400" ] || [ "$HTTP_CODE" = "422" ]; then
    echo -e "${GREEN}✓ Correctly returned ${HTTP_CODE} for invalid IP${NC}"
else
    echo -e "${RED}✗ Expected 400/422, got HTTP ${HTTP_CODE}${NC}"
    echo "$RESPONSE"
fi
echo ""

echo "========================================="
echo "Test suite completed!"
echo "========================================="
