# Via Node API Test Scripts

This directory contains scripts to test the Via Node REST API endpoints.

## Test Scripts

### Topology CRUD (`test_topology_api.sh`)

Tests core topology CRUD API endpoints.

### Discovery & Scanning (`test_discovery_api.sh`)

Tests discovery and scanning API endpoints:
- ✓ Discover DNS records for a domain
- ✓ Discover DNS records with specific record types
- ✓ Invalid record type validation (400)
- ✓ Discover subdomains
- ✓ Scan ports with specific ports
- ✓ Scan ports with default port range

---

## Bash Test Script (`test_topology_api.sh`)

A comprehensive bash script that tests all topology CRUD API endpoints.

**Requirements:**
- `curl`
- `jq` (optional, for pretty JSON output)

**Authentication:**
The script uses HTTP Basic Authentication with default credentials:
- Username: `admin`
- Password: `password`

To use different credentials, set environment variables:
```bash
export VIA_NODE_USER=myuser
export VIA_NODE_PASSWORD=mypass
```

**Usage:**
```bash
# Test against local server (default: http://localhost:8000)
./test_topology_api.sh

# Test against a different server
./test_topology_api.sh http://production-server:8080

# Test with custom credentials
VIA_NODE_USER=myuser VIA_NODE_PASSWORD=mypass ./test_topology_api.sh
```

**What it tests:**
- ✓ Create host
- ✓ Get host by IP
- ✓ Create domain-port edge
- ✓ Create DNS-resolves-to-host edge
- ✓ Get port
- ✓ Get DNS record
- ✓ Get non-existent host (404 validation)
- ✓ Create host with invalid IP (400 validation)

## Bash Test Script (`test_discovery_api.sh`)

A bash script that tests discovery and scanning API endpoints.

**Usage:**
```bash
# Test against local server (default: http://localhost:8000)
./test_discovery_api.sh

# Test against a different server
./test_discovery_api.sh http://production-server:8080

# Test with custom credentials
VIA_NODE_USER=myuser VIA_NODE_PASSWORD=mypass ./test_discovery_api.sh
```

**What it tests:**
- ✓ Discover DNS records
- ✓ Discover DNS records with specific types (A, AAAA, MX)
- ✓ Invalid record type validation (400)
- ✓ Discover subdomains
- ✓ Scan ports with specific ports
- ✓ Scan ports with default range

## Starting the API Server

Before running the tests, you need to start the Via Node API server:

```bash
# From the project root directory

# Option 1: Using uvicorn directly
uvicorn via_node.interface.api.main:app --reload

# Option 2: Using the run script (if available)
./run.sh

# Option 3: With custom host/port
uvicorn via_node.interface.api.main:app --host 0.0.0.0 --port 8080
```

## Expected Output

Both scripts will output colored results:
- 🟢 **Green** - Test passed
- 🔴 **Red** - Test failed  
- 🟡 **Yellow** - Warning or informational message

Example:
```
=========================================
Via Node Topology API Test Suite
=========================================
Base URL: http://localhost:8000
API Base: http://localhost:8000/api/v1

Test 1: Create Host
✓ Host created successfully (HTTP 201)
  Location: /api/v1/hosts/192.168.1.100

Test 2: Get Host by IP
✓ Host retrieved successfully (HTTP 200)
{
  "ip_address": "192.168.1.100",
  "hostname": "test-server.example.com",
  "os_type": "Linux",
  ...
}

...

=========================================
Test suite completed!
=========================================
```

## Troubleshooting

**Connection refused:**
- Make sure the API server is running
- Check that you're using the correct URL and port

**404 errors:**
- The API server is running but endpoints are not registered
- Check that the topology controller is properly wired in `main.py`

**Authentication errors (401/403):**
- The test scripts don't currently include authentication
- If your API requires auth, you'll need to add credentials to the scripts

**500 Internal Server Error:**
- Check the API server logs for details
- Verify that ArangoDB is running and accessible
- Ensure all dependencies are properly configured

## Extending the Tests

To add more test cases to the bash script:

```bash
# Add a new test function
echo -e "${YELLOW}Test N: Your Test Name${NC}"
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/your-endpoint")
HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓ Your test passed${NC}"
else
    echo -e "${RED}✗ Your test failed (HTTP ${HTTP_CODE})${NC}"
    echo "$RESPONSE"
fi
```

## CI/CD Integration

This script can be used in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Test API endpoints
  run: ./test-scripts/test_topology_api.sh http://localhost:8000
```

```bash
# Example Jenkins pipeline
sh './test-scripts/test_topology_api.sh http://staging-server:8000'
```

The script returns proper exit codes (0 for success, non-zero for failure) making it suitable for automated testing.
