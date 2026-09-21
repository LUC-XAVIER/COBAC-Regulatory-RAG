import sys
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def main():
    return "Hello from COBAC-CEMAC-BEAC-regulatory-rag!"


if __name__ == "__main__":
    main()
