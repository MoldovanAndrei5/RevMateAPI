from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from routes.car_routes import router as car_router
from routes.task_routes import router as task_router
from routes.auth_routes import router as auth_router
from routes.transfer_routes import router as transfer_router
from routes.invoice_routes import router as invoice_router
from routes.upload_routes import router as upload_router

def create_app() -> FastAPI:
    app = FastAPI(title="Car Maintenance Tracker")

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
    app.include_router(transfer_router, prefix="/transfers", tags=["Transfers"])
    app.include_router(invoice_router, prefix="/invoices", tags=["Invoices"])
    app.include_router(upload_router, prefix="/upload", tags=["Upload"])

    @app.get("/")
    def root():
        return {"message": "Welcome to Car Maintenance Tracker!"}

    @app.get("/health")
    def health_check():
        return {"status": "Healthy"}

    return app