# AI Network Diagnostic API

An API for classifying network diagnostics using AI.

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your OpenAI API key in an environment variable:
   ```bash
   set OPENAI_API_KEY=your-api-key
   ```

## Running the API

```bash
python -m uvicorn src.main:app --reload
```

The API will be available at http://127.0.0.1:8000

## API Documentation

Once the server is running, visit:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### Endpoints

#### 1. Multi-step Diagnostic

`POST /api/v1/diagnose`

Analyze multiple diagnostic steps and their results to classify the issue.

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "steps": [
      {
        "step": "Check interface status",
        "result": "Interface GigabitEthernet1/0/1 is down"
      },
      {
        "step": "Verify UNI equipment",
        "result": "UNI device XYZ123 is unreachable"
      }
    ]
  }'
```

#### 2. Single-step Diagnostic

`POST /api/v1/diagnose/single`

Analyze a single description to classify the issue.

**Example Request:**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/diagnose/single \
  -H "Content-Type: application/json" \
  -d '{
    "description": "The interface GigabitEthernet1/0/1 is down and the UNI device XYZ123 is unreachable"
  }'
```

### Example Response (for both endpoints)

```json
{
  "category_id": 1,
  "category_name": "Puerto LAN",
  "category_description": "Determina si existe una falla real que pueda ser atribuida a la caída de un equipo UNI..."
}

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

## License

MIT
