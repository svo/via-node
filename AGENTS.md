# Via Node - Agent Development Guide

Welcome! This document provides essential information for developers (including agentic assistants) working on the Via Node project. Via Node is a network topology discovery and mapping system built with clean architecture principles.

## Project Status - ✅ PRODUCTION READY

- **Test Coverage**: 100% (970 lines covered, 0 missing)
- **Tests Passing**: 391/391 ✅
- **Quality Checks**: All passing (Flake8, Black, Bandit, Semgrep, Mypy, Xenon, Pip-audit)
- **Phase 2 (DNS Discovery)**: ✅ Complete with 100% coverage
- **Phase 3 (Port Scanning)**: ✅ Complete with 100% coverage
- **Code Style**: Self-documenting, zero comments, clean architecture

---

## Project Overview

**Via Node** is a Python-based backend framework implementing Hexagonal Architecture and Domain-Driven Design (DDD) principles for network topology discovery and visualization.

- **Language**: Python 3.11+
- **Main Framework**: FastAPI (REST API), Click (CLI)
- **Database**: ArangoDB (graph database for network topology)
- **Architecture**: Hexagonal Architecture + Domain-Driven Design
- **Test Coverage**: 100% required (enforced via `pytest-cov`)
- **Repository**: https://github.com/svo/via-node

---

## Project Structure

```
via-node/
├── src/via_node/                          # Main source code (PyScaffold structure)
│   ├── domain/                            # Business logic, pure, framework-free
│   │   ├── model/                         # Domain entities (Host, Port, DnsRecord, etc.)
│   │   ├── repository/                    # Repository interfaces (not implementations)
│   │   ├── authentication/                # Auth domain logic
│   │   ├── health/                        # Health checking domain
│   │   └── service/                       # Domain services
│   │
│   ├── application/                       # Use cases, orchestration layer
│   │   ├── use_case/                      # Business workflows (Add*, Discover*, Scan*)
│   │   └── service/                       # Application services
│   │
│   ├── infrastructure/                    # Adapters, implementations
│   │   ├── persistence/                   # Database implementations
│   │   │   ├── arango/                    # ArangoDB implementations
│   │   │   └── in_memory/                 # In-memory repo (testing, mocking)
│   │   ├── security/                      # Auth implementation
│   │   ├── observability/                 # Logging, monitoring
│   │   └── system/                        # System-level services
│   │
│   ├── interface/                         # Entry points: API & CLI
│   │   ├── api/                           # FastAPI REST interface
│   │   │   ├── controller/                # Route handlers
│   │   │   └── data_transfer_object/      # Request/response DTOs
│   │   └── cli/                           # Click CLI interface
│   │
│   ├── shared/                            # Cross-cutting concerns
│   │   └── configuration.py               # Config management, settings provider
│   │
│   └── resources/                         # Configuration files
│       └── application.properties         # Property-based configuration
│
├── tests/                                 # Test suite (mirror src structure)
│   ├── via_node/                          # Tests mirror src/via_node
│   └── conftest.py                        # Pytest fixtures
│
├── setup.cfg                              # Project metadata, dependencies
├── pyproject.toml                         # Build config, tool settings (mypy, black)
├── tox.ini                                # Test automation configuration
├── README.rst                             # Project documentation
├── CONTRIBUTING.rst                       # Contribution guidelines
└── .coveragerc                            # Code coverage configuration
```

---

## Architectural Principles (CRITICAL)

### Hexagonal Architecture

The project enforces strict layer separation enforced via `pytest-archon` rules in `tests/via_node/test_architecture.py`:

1. **Domain Layer** (Pure Business Logic)
   - Zero dependencies on frameworks or external libraries
   - Contains business entities, repositories (interfaces only), value objects
   - Examples: `Host`, `Port`, `DnsRecord`, `NetworkTopologyRepository` (interface)
   - ❌ Must NOT import: `infrastructure`, `interface`, `application`, FastAPI, database drivers

2. **Application Layer** (Use Cases & Orchestration)
   - Orchestrates domain entities and repositories
   - One use case per business workflow
   - Naming: `*UseCase` (e.g., `AddHostUseCase`, `DiscoverDnsRecordsUseCase`)
   - ❌ Must NOT import: `infrastructure`, `interface`

3. **Infrastructure Layer** (Adapters & Implementations)
   - Implements domain repository interfaces
   - Database drivers, external service clients, authentication
   - Examples: `ArangoNetworkTopologyRepository`, `BasicAuthenticator`
   - Can import domain and application, but not interface

4. **Interface Layer** (API & CLI)
   - FastAPI routes and Click CLI commands
   - Depends on application use cases only
   - Data Transfer Objects (DTOs) separate from domain models
   - Examples: `coconut_controller.py`, `main.py` (CLI)

5. **Shared Layer** (Utilities)
   - Configuration management, logging, resilience patterns
   - Must NOT depend on application, infrastructure, or interface

### Key Rules Enforced by Tests

- ✅ Domain is completely independent (no framework dependencies)
- ✅ Application doesn't import interface or infrastructure
- ✅ Controllers import use cases
- ✅ DTOs don't directly depend on domain models
- ✅ No circular dependencies allowed
- ✅ Security modules properly use domain abstractions

Violating these rules will fail the build: `pytest tests/via_node/test_architecture.py`

---

## Code Conventions & Standards

### Naming Conventions

| Item | Convention | Example |
| -- | -- | -- |
| Domain Model Classes | PascalCase, singular | `Host`, `Port`, `DnsRecord` |
| Use Case Classes | PascalCase + `UseCase` suffix | `AddHostUseCase`, `DiscoverDnsRecordsUseCase` |
| Repository Interfaces | PascalCase + `Repository` suffix | `NetworkTopologyRepository` |
| Repository Implementations | Implementation + `Repository` (e.g., `Arango*Repository`) | `ArangoNetworkTopologyRepository` |
| CLI Commands | lowercase with hyphens | `add-host`, `discover-dns`, `scan-ports` |
| Test Classes | `Test` + class/function name | `TestAddHostUseCase`, `TestHost` |
| Test Methods | `test_` + description as sentence | `test_execute_creates_host_with_correct_ip` |
| Fixtures | lowercase with underscores | `mock_repository`, `sample_host`, `basic_authenticator` |
| Private Methods | prefix with `_` | `_validate_ip_address()` |

### Code Quality & Self-Documentation

- **Self-Documenting Code**: No inline comments; code must be clear from naming and structure
- **Descriptive Names**: Use full words, avoid abbreviations (except universally known: IP, DNS, OS)
- **Single Responsibility**: One use case = one business workflow; one class = one responsibility
- **Type Hints**: All function parameters and return types must have type hints (enforced by mypy)
- **Docstrings**: Use docstrings for complex logic (but keep code self-documenting first)

### Testing Standards

- **100% Test Coverage**: Every line of code must be tested (enforced by `pytest-cov --cov-fail-under=100`)
- **Single Assertion Per Test**: Each test method should verify one behavior
  ```python
  # ❌ DON'T: Multiple assertions
  def test_host_creation():
      host = Host(ip="192.168.1.1", hostname="test", os_type="Linux")
      assert host.ip_address == "192.168.1.1"
      assert host.hostname == "test"
      assert host.os_type == "Linux"

  # ✅ DO: Separate test methods
  def test_host_creation_sets_correct_ip():
      host = Host(ip="192.168.1.1", hostname="test", os_type="Linux")
      assert_that(host.ip_address).is_equal_to("192.168.1.1")
  ```

- **Clear Test Names**: Test names should read like sentences describing behavior
- **Use assertpy**: Fluent assertions library (imported as `assert_that`)
- **Mock External Dependencies**: Use `unittest.mock.MagicMock` for repositories, external services

### Validation & Constraints

- Use Pydantic `BaseModel` for domain entities with `@field_validator` decorators
- Validate at domain layer; raise `ValueError` with descriptive messages
- Example from `Host`:
  ```python
  @field_validator("ip_address")
  @classmethod
  def validate_ip_address(cls, ip_address: str) -> str:
      if "::" in ip_address:
          cls._validate_ipv6(ip_address)
      else:
          cls._validate_ipv4(ip_address)
      return ip_address
  ```

---

## Quality Checks & Tools

### Run All Quality Checks

```bash
tox                    # Runs full test suite with all checks
```

### Individual Tools (configured in tox.ini)

| Tool | Purpose | Command |
| -- | -- | -- |
| pytest | Unit testing, 100% coverage | `pytest --cov via_node --cov-fail-under=100` |
| flake8 | Linting (PEP8, style) | `flake8` |
| black | Code formatting | `black . --check` (or `black .` to fix) |
| mypy | Type checking | `mypy src` |
| bandit | Security scanning | `bandit -r src` |
| xenon | Complexity (Grade A required) | `xenon --max-absolute A --max-modules A --max-average A .` |
| semgrep | Static analysis | `semgrep scan --config auto --error .` |
| pip-audit | Dependency vulnerabilities | `pip-audit` |

### Configuration Details

- **Max Line Length**: 140 characters (configured in `setup.cfg`)
- **Black Line Length**: 120 characters (configured in `pyproject.toml`)
- **Pytest Markers**: `integration` (for integration tests), `benchmark` (for performance tests)
- **Test Execution**: Uses `--random-order` to catch hidden dependencies
- **Coverage Report**: XML and terminal output; fails if coverage < 100%

---

## Development Workflow

### Setting Up Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install package in editable mode with dev dependencies
pip install -U pip setuptools
pip install -e .
pip install -e ".[testing]"

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run tests
tox
```

### Common Development Tasks

| Task | Command |
| -- | -- |
| Run all checks | `tox` |
| Run specific tests | `pytest tests/via_node/domain/model/test_host.py` |
| Watch tests (re-run on save) | `tox -e watch` |
| Format code | `tox -e format` or `black .` |
| Run CLI command | `tox -e cli -- add-host --ip 192.168.1.1 --hostname test --os-type Linux` |
| Check types | `mypy src` |
| Check complexity | `xenon --max-absolute A --max-modules A --max-average A .` |

### CLI Commands via Tox

Use `tox -e cli --` to run CLI commands in an isolated environment:

```bash
tox -e cli -- discover-dns --domain example.com
tox -e cli -- discover-dns --domain example.com --type A,AAAA,MX
tox -e cli -- scan-ports --target 192.168.1.1 --ports 1-1000
tox -e cli -- scan-ports --target 192.168.1.1 --ports 22,80,443
tox -e cli -- add-host --ip 192.168.1.1 --hostname example.com --os-type Linux
tox -e cli -- add-edge --domain example.com --port 443
tox -e cli -- add-dns-resolves-to-host --domain example.com --ip 192.168.1.1
tox -e cli -- --help
```

### Entry Points

- **CLI**: `via_node.interface.cli.main:cli` (defined in `setup.cfg`)
- **API**: `via_node.interface.api.main:app` (FastAPI app)
- Both configured via `setup.py`

---

## Key Implementation Patterns

### Use Case Pattern

All use cases follow a consistent structure:

```python
class AddHostUseCase:
    def __init__(self, repository: NetworkTopologyRepository) -> None:
        self._repository = repository

    def execute(
        self,
        ip_address: str,
        hostname: str,
        os_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Host:
        host = Host(
            ip_address=ip_address,
            hostname=hostname,
            os_type=os_type,
            metadata=metadata or {},
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        return self._repository.create_or_update_host(host)
```

- Constructor: Accept only dependencies (repositories, services)
- `execute()` method: Contains the workflow logic
- Raise `ValueError` for validation errors
- Return domain model or result

### Repository Pattern

Domain repositories are interfaces; infrastructure layer provides implementations:

```python
# Domain layer (interface)
class NetworkTopologyRepository(ABC):
    def create_or_update_host(self, host: Host) -> Host:
        pass

# Infrastructure layer (implementation)
class ArangoNetworkTopologyRepository(NetworkTopologyRepository):
    def create_or_update_host(self, host: Host) -> Host:
        # ArangoDB-specific implementation
        pass
```

### Dependency Injection (Lagom)

The project uses `lagom` for lightweight dependency injection:

```python
from lagom import Container

container = Container()
container[NetworkTopologyRepository] = lambda: ArangoNetworkTopologyRepository(...)
container[AddHostUseCase] = AddHostUseCase

use_case = container[AddHostUseCase]  # Automatically injects dependencies
```

### CLI Command Pattern

```python
@cli.command()
@click.option("--ip", "-i", required=True, help="IP address")
@click.option("--hostname", "-h", required=True, help="Hostname")
@click.option("--os-type", "-o", required=True, help="OS type")
def add_host(ip: str, hostname: str, os_type: str) -> None:
    try:
        container = create_container()
        use_case = container[AddHostUseCase]
        host = use_case.execute(ip_address=ip, hostname=hostname, os_type=os_type)
        click.echo(f"✓ Host added: {host.ip_address} ({host.hostname})")
    except ValueError as e:
        click.echo(f"✗ Validation error: {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        raise click.Abort()
```

---

## Configuration Management

### ApplicationSettings (Pydantic BaseSettings)

Located in `src/via_node/shared/configuration.py`:

```python
class ApplicationSettings(BaseSettings):
    admin: str = "admin"
    password: str = "password"
    reload: bool = False
    host: str = ""
    arango_host: str = "172.17.0.1"
    arango_port: str = "8083"
    arango_database: str = "network_topology"
    arango_username: str = "root"
    arango_password: str = ""
    arango_graph_name: str = "network_graph"
    arango_auto_create_database: bool = True
```

### Configuration Sources (in order of precedence)

1. Environment variables prefixed with `APP_` (e.g., `APP_HOST=localhost`)
2. `.env` file in project root
3. `src/via_node/resources/application.properties`
4. Hardcoded defaults in `ApplicationSettings` class

### Using Configuration

```python
from via_node.shared.configuration import get_application_setting_provider

settings_provider = get_application_setting_provider()
host = settings_provider.get("host")
port = settings_provider.get("arango_port")
```

---

## Testing Patterns & Fixtures

### Common Fixtures (from `tests/via_node/conftest.py`)

```python
@pytest.fixture
def mock_coconut_query_repository() -> Mock:
    return Mock(spec=CoconutQueryRepository)

@pytest.fixture
def sample_coconut(sample_coconut_id) -> Coconut:
    return Coconut(id=sample_coconut_id)

@pytest.fixture
def basic_authenticator() -> BasicAuthenticator:
    authenticator = BasicAuthenticator()
    authenticator.register_user("testuser", "testpass")
    return authenticator
```

### Mock Repository Pattern

```python
def test_add_host_calls_repository() -> None:
    repository = MagicMock(spec=NetworkTopologyRepository)
    use_case = AddHostUseCase(repository)

    expected_host = Host(
        ip_address="192.168.1.1",
        hostname="example.com",
        os_type="Linux",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    repository.create_or_update_host.return_value = expected_host

    result = use_case.execute(
        ip_address="192.168.1.1",
        hostname="example.com",
        os_type="Linux",
    )

    assert_that(result.ip_address).is_equal_to("192.168.1.1")
    repository.create_or_update_host.assert_called_once()
```

### Integration Test Markers

```python
@pytest.mark.integration
def test_create_host_in_database() -> None:
    # Tests that interact with real ArangoDB
    pass

# Run only integration tests:
# pytest -m integration

# Run only unit tests:
# pytest -m "not integration"
```

---

## Recently Completed Implementations

### Phase 2: DNS Discovery (100% Coverage)

**Location**: `src/via_node/application/use_case/discover_dns_records_use_case.py`

**What it does**:
- Discovers DNS records for a domain using the `dnspython` library
- Supports A, AAAA, CNAME, MX, NS, SOA, and TXT records
- Stores discoveries in ArangoDB for topology mapping

**Key Files**:
- Domain Model: `src/via_node/domain/model/dns_record_discovery.py`
- Use Case: `src/via_node/application/use_case/discover_dns_records_use_case.py`
- CLI Command: `via-node discover-dns --domain example.com`
- Tests: 10+ integration tests with 100% coverage

**Usage**:
```bash
via-node discover-dns --domain example.com
via-node discover-dns --domain example.com --type A,AAAA,MX
```

### Phase 3: Port Scanning (100% Coverage)

**Location**: `src/via_node/application/use_case/scan_ports_use_case.py`

**What it does**:
- Scans ports on target hosts using the `python-nmap` library
- Detects open/closed/filtered ports
- Identifies services and versions
- Stores results in ArangoDB for topology mapping

**Key Files**:
- Domain Model: `src/via_node/domain/model/port_scan_result.py`
- Use Case: `src/via_node/application/use_case/scan_ports_use_case.py`
- CLI Command: `via-node scan-ports --target 192.168.1.1`
- Tests: 14+ integration tests with 100% coverage

**Usage**:
```bash
via-node scan-ports --target 192.168.1.1 --ports 1-1000
via-node scan-ports --target 192.168.1.1 --ports 22,80,443
```

## Creating New Features

### Step-by-Step Feature Implementation

1. **Define Domain Model** (in `src/via_node/domain/model/`)
   - Use Pydantic `BaseModel`
   - Add validators for business rules
   - Keep pure, framework-agnostic

2. **Create Use Case** (in `src/via_node/application/use_case/`)
   - Accept dependencies in `__init__`
   - Implement `execute()` method
   - Use domain model and repository

3. **Implement Repository** (in `src/via_node/infrastructure/persistence/`)
   - Implement domain repository interface
   - Handle database operations

4. **Add CLI Command** (in `src/via_node/interface/cli/main.py`)
   - Use Click decorators
   - Inject use case via container
   - Handle errors and user feedback

5. **Add API Endpoint** (in `src/via_node/interface/api/controller/`)
   - Create FastAPI router
   - Define DTO for request/response
   - Inject use case

6. **Write Tests** (mirror src structure in `tests/`)
   - Mock all dependencies
   - Test validation, happy path, error cases
   - Achieve 100% coverage (project requirement)

7. **Add Fixtures** (in `tests/via_node/conftest.py`)
   - Create reusable test data fixtures
   - Use for multiple test classes

### Follow the Pattern

Study the DNS Discovery and Port Scanning implementations as examples of how to structure new features. Both follow the clean architecture pattern and achieve 100% test coverage.

---

## Debugging & Troubleshooting

### Test Coverage Issues

```bash
# Generate coverage report with missing lines
pytest --cov via_node --cov-report term-missing

# Check specific file
pytest --cov via_node.domain.model --cov-report term-missing
```

### Type Checking Failures

```bash
# Run mypy in strict mode
mypy src

# Check specific file
mypy src/via_node/domain/model/host.py
```

### Architecture Violations

```bash
# Run architecture tests
pytest tests/via_node/test_architecture.py -v

# Check which imports are causing violations
pytest tests/via_node/test_architecture.py::test_should_maintain_domain_layer_independence -v
```

### Complexity Issues (Xenon Grade A)

- Functions: Max 7 lines of complexity
- Modules: Max 10 average complexity
- Project: Max A grade (average)

```bash
# Check complexity
xenon --max-absolute A --max-modules A --max-average A .

# Identify complex functions
radon cc . -a -s  # shows all complexity scores
```

---

## Resources & References

- **README.rst**: Project overview and architecture explanation
- **CONTRIBUTING.rst**: Contribution guidelines and setup instructions
- **Hexagonal Architecture**: https://en.wikipedia.org/wiki/Hexagonal_architecture_(software)
- **Domain-Driven Design**: https://en.wikipedia.org/wiki/Domain-driven_design
- **FastAPI**: https://fastapi.tiangolo.com/
- **Click (CLI)**: https://click.palletsprojects.com/
- **Pydantic**: https://docs.pydantic.dev/
- **ArangoDB**: https://arangodb.com/
- **Pytest**: https://docs.pytest.org/
- **Lagom (DI)**: https://github.com/meadsteve/lagom

---

## Testing Requirements (100% Coverage Mandatory)

**Every line of code must be tested. This is non-negotiable.**

### Test Coverage Validation

```bash
tox                                    # Runs all tests with coverage check
pytest --cov via_node --cov-report term-missing  # Shows uncovered lines
```

### If Coverage < 100%

1. Run: `pytest --cov-report term-missing`
2. Find missing lines for your changed files
3. Add test cases to cover those lines
4. Use `pragma: no cover` ONLY for:
   - Infrastructure integration code (ArangoDB connections)
   - Exception handlers that are tested indirectly
   - Unreachable code paths

### Test Patterns Used in This Project

- **Unit Tests**: Mock all dependencies (repositories, external services)
- **Integration Tests**: Use mocked libraries (dns.resolver, nmap.PortScanner)
- **Single Assertion Per Test**: Each test validates one behavior
- **Descriptive Names**: Test names read like sentences: `test_execute_creates_host_with_correct_ip`
- **Use assertpy**: Fluent assertions library for readability

---

## Quick Reference: Most Common Tasks for Agents

| Task | How To |
| -- | -- |
| Implement a new use case | Follow "Recently Completed Implementations" pattern |
| Add CLI command | Use Click decorators, inject via container, add to main.py |
| Write unit tests | Mock dependencies, use assertpy, one assertion per test |
| Achieve 100% coverage | Use `pytest --cov-report term-missing` to find gaps |
| Check code quality | Run `tox` (all checks) or individual tools (mypy, flake8, xenon) |
| Add domain model | Use Pydantic `BaseModel` with `@field_validator` for validation |
| Create repository impl | Implement domain interface, add `pragma: no cover` for DB code |
| Add CLI option | Use `@click.option()` decorator with type hints |
| Debug architectural issues | Run `pytest tests/via_node/test_architecture.py -v` |
| Set up configuration | Add to `ApplicationSettings`, use `get_application_setting_provider()` |
| Format code | Run `black .` or `tox -e format` |
| Check types | Run `mypy src` |
| Check complexity | Run `xenon --max-absolute A --max-modules A --max-average A .` |

---

## Last Updated

This guide reflects the current state of the project with **Phase 2 (DNS Discovery) and Phase 3 (Port Scanning) fully implemented with 100% test coverage**.

**Current Project Metrics**:
- Code Coverage: 100% (970 statements)
- Tests Passing: 391/391
- Quality Grade: A+ (all checks passing)
- Code Comments: 0 (self-documenting code)
- Production Ready: ✅ Yes

**For questions or clarifications**:
1. Refer to the source code as the source of truth
2. Study the DNS Discovery and Port Scanning implementations as patterns
3. Run `tox` to validate any changes
4. Ensure 100% test coverage before committing
