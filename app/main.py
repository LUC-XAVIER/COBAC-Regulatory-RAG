import sys
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def main():
    return "Hello from cobac-regulatory-rag!"


if __name__ == "__main__":
    main()
