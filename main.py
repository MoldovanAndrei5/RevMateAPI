from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from starlette.testclient import TestClient
import json

from database import engine
from routes.car_routes import router as car_router
from routes.task_routes import router as task_router
from routes.auth_routes import router as auth_router
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Car Maintenance Tracker")
# hello world 2
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(car_router, prefix="/cars", tags=["Cars"])
app.include_router(task_router, prefix="/tasks", tags=["Tasks"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
# hello world
@app.get("/")
def root():
    return {"message": "Welcome to Car Maintenance Tracker!"}

@app.get("/health")
async def health_check():
    return {"status": "Healthy"}


def handler(event, context):
    method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "GET")
    path = event.get("path") or event.get("rawPath", "/")
    query = event.get("queryStringParameters") or {}
    headers = event.get("headers") or {}
    body = event.get("body") or ""
    
    print(f"[DEBUG] Raw event: {json.dumps(event)}")
    print(f"[DEBUG] Body type: {type(body)}")
    print(f"[DEBUG] Body value: {body}")

    print(f"[LAMBDA REQUEST] {method} {path}")

    if event.get("isBase64Encoded") and body:
        import base64
        body = base64.b64decode(body)
    elif isinstance(body, str) and body:
        body = body.encode("utf-8")  # convert string to bytes

    client = TestClient(app, raise_server_exceptions=False)

    response = client.request(
        method=method,
        url=path,
        params=query,
        headers=headers,
        content=body if body else None,
    )

    print(f"[LAMBDA RESPONSE] Status: {response.status_code}")

    return {
        "statusCode": response.status_code,
        "headers": dict(response.headers),
        "body": response.text,
        "isBase64Encoded": False,
    }
# -------------------------------
# Local dev
# -------------------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)