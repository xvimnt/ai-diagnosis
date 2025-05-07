from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from dotenv import load_dotenv
from src.infrastructure.ai_diagnostic_classifier import AIDiagnosticClassifier

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="AI Network Diagnostic API",
    description="API for classifying network diagnostics using AI",
    version="1.0.0"
)

class DiagnosticStep(BaseModel):
    step: str
    result: str

class DiagnosticRequest(BaseModel):
    steps: List[DiagnosticStep]

class SingleStepRequest(BaseModel):
    description: str

class DiagnosticResponse(BaseModel):
    category_id: int
    category_name: str
    category_description: str

@app.post("/api/v1/diagnose", response_model=DiagnosticResponse)
async def diagnose(request: DiagnosticRequest) -> DiagnosticResponse:
    """Analyze multiple diagnostic steps and classify the issue."""
    try:
        classifier = AIDiagnosticClassifier()
        diagnostic_input = {"steps": [step.model_dump() for step in request.steps]}
        
        category_id = await classifier.classify_diagnostic(diagnostic_input)
        category = classifier.diagnostic_rules.get(category_id)
        
        if not category:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid category ID returned: {category_id}"
            )
            
        return DiagnosticResponse(
            category_id=category_id,
            category_name=category["name"],
            category_description=category["description"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/v1/diagnose/single", response_model=DiagnosticResponse)
async def diagnose_single(request: SingleStepRequest) -> DiagnosticResponse:
    """Analyze a single description and classify the issue."""
    try:
        classifier = AIDiagnosticClassifier()
        category_id = await classifier.classify_single_step(request.description)
        category = classifier.diagnostic_rules.get(category_id)
        
        if not category:
            raise HTTPException(
                status_code=500,
                detail=f"Invalid category ID returned: {category_id}"
            )
            
        return DiagnosticResponse(
            category_id=category_id,
            category_name=category["name"],
            category_description=category["description"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
