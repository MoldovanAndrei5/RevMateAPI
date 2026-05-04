import uvicorn
from database import engine
from app import create_app
import models

models.Base.metadata.create_all(bind=engine)

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)