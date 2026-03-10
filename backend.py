from fastapi import FastAPI
from pydantic import BaseModel
from agent import run_analysis
import os

app = FastAPI(title="Finance Analysis API")


class AnalysisRequest(BaseModel):
    month: str
    year: int
    currency: str


class AnalysisResponse(BaseModel):
    result: str


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(request: AnalysisRequest):
    result = run_analysis(month=request.month, year=request.year, currency=request.currency)
    return AnalysisResponse(result=result)


# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("backend:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("backend:app", host="0.0.0.0", port=port)