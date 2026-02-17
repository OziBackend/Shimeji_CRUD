import uvicorn
from environment.config import SYSTEM_PORT, SYSTEM_IP

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=SYSTEM_IP,
        port=SYSTEM_PORT,
        reload=True
    )