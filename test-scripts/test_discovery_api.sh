#!/bin/bash
#
# Test script for Via Node Discovery & Scanning REST API
# 
# Usage: ./test_discovery_api.sh [BASE_URL]
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
echo "Via Node Discovery & Scanning API Tests"
echo "========================================="
echo "Base URL: ${BASE_URL}"
echo "API Base: ${API_BASE}"
echo "Username: ${USERNAME}"
echo ""

# Test 1: Discover DNS records for a domain
echo -e "${YELLOW}Test 1: Discover DNS Records${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X POST "${API_BASE}/discover/dns" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "example.com"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ DNS discovery completed successfully (HTTP 200)${NC}"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ DNS discovery failed (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 2: Discover DNS records with specific record types
echo -e "${YELLOW}Test 2: Discover DNS Records with Specific Types${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X POST "${API_BASE}/discover/dns" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "example.com",
    "record_types": ["A", "AAAA", "MX"]
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ DNS discovery with types completed successfully (HTTP 200)${NC}"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ DNS discovery with types failed (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 3: Discover DNS records with invalid record type (should return 400)
echo -e "${YELLOW}Test 3: Discover DNS with Invalid Record Type (should return 400)${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X POST "${API_BASE}/discover/dns" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "example.com",
    "record_types": ["INVALID"]
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "400" ]; then
    echo -e "${GREEN}✓ Correctly returned 400 for invalid record type${NC}"
else
    echo -e "${RED}✗ Expected 400, got HTTP ${HTTP_CODE}${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 4: Discover subdomains
echo -e "${YELLOW}Test 4: Discover Subdomains${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X POST "${API_BASE}/discover/subdomains" \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "example.com"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Subdomain discovery completed successfully (HTTP 200)${NC}"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ Subdomain discovery failed (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 5: Scan ports on a target
echo -e "${YELLOW}Test 5: Scan Ports${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X POST "${API_BASE}/scan/ports" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "127.0.0.1",
    "ports": "22,80,443"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Port scan completed successfully (HTTP 200)${NC}"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ Port scan failed (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

# Test 6: Scan ports with default port range
echo -e "${YELLOW}Test 6: Scan Ports with Default Range${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -u "${USERNAME}:${PASSWORD}" -X POST "${API_BASE}/scan/ports" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "127.0.0.1"
  }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
BODY=$(echo "$RESPONSE" | head -n -1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Port scan with defaults completed successfully (HTTP 200)${NC}"
    echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"
else
    echo -e "${RED}✗ Port scan with defaults failed (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
echo ""

echo "========================================="
echo "Discovery & Scanning test suite completed!"
echo "========================================="
