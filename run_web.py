
"""Run the MockAgent web server."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "mockagent.api.app:create_app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1,
    )

