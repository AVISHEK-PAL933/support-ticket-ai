from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .query_service import QueryService
from .anomaly_service import AnomalyService


app = FastAPI(
    title="AI Customer Support Ticket System",
    description="AI-powered customer support ticket analytics API",
    version="1.0.0"
)

app.mount("/ui", StaticFiles(directory="ui", html=True), name="ui")
query_service = QueryService()
anomaly_service = AnomalyService()


class QueryRequest(BaseModel):
    question: str


@app.get("/")
def root():
    return {
        "message": "AI Customer Support Ticket System is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/query")
def natural_language_query(request: QueryRequest):

    result = query_service.execute_question(
        request.question
    )

    return result


@app.get("/anomalies")
def detect_anomalies():

    return anomaly_service.detect_all_anomalies()