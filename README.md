# Network Diagnostic System

A Python-based diagnostic system for network services that follows SOLID principles and implements Test-Driven Development (TDD).

## Features

- Asynchronous diagnostic process
- Service and circuit validation
- Concurrent device diagnostics
- Root cause analysis
- Notification system
- Error handling and logging
- SNMP device monitoring

## Project Structure

```
ai-diagnosis/
├── src/
│   ├── domain/           # Domain entities and business logic
│   ├── application/      # Application services and use cases
│   └── infrastructure/   # External services implementation
├── tests/                # Test files
└── requirements.txt      # Project dependencies
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Tests

There are several ways to run the tests:

1. Using pytest directly:
```bash
python -m pytest
```

2. Using the provided batch script:
```bash
run_tests.bat
```

3. Using specific test files or test cases:
```bash
python -m pytest tests/test_diagnostic_process.py -k test_initialize_diagnostic_process -v
```

The project uses pytest.ini configuration that:
- Sets strict asyncio mode for async/await testing
- Sets the fixture loop scope to function level
- Shows verbose output
- Shows locals on test failures
- Automatically finds and runs all test files in the tests directory

## Design Patterns Used

- **Strategy Pattern**: For different diagnostic strategies based on device vendors
- **Observer Pattern**: For notification system
- **Repository Pattern**: For data access abstraction
- **Factory Pattern**: For creating diagnostic processes

## SOLID Principles Implementation

1. **Single Responsibility Principle**: Each class has a single responsibility (e.g., DiagnosticProcess, DeviceService)
2. **Open/Closed Principle**: New diagnostic strategies can be added without modifying existing code
3. **Liskov Substitution Principle**: Different service implementations can be substituted without affecting the system
4. **Interface Segregation**: Clients are not forced to depend on interfaces they don't use
5. **Dependency Inversion**: High-level modules depend on abstractions

## License

MIT
