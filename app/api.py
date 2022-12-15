from fastapi import FastAPI, status
import uvicorn

from database import create_engine

from validation_schema.validate import Register, Delete, ListRegister

# Creating database engine
create_engine.create_database_engine()

# FastAPI app
app = FastAPI()


@app.get("/health")
def root():
    return {"message": "Hello World"}


@app.get("/report")
def report():
    return {}


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(register: ListRegister):
    registers = [dict(element) for element in register.registers]
    return f" These registers was reiceved: {registers}"


@app.put("/update")
def update(update: Register):
    return {}


@app.delete("/delete")
def delete(delete: Delete):
    return {}


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=5000, reload=True, workers=1)
