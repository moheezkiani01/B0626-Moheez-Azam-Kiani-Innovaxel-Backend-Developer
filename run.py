import webbrowser
import uvicorn

if __name__ == "__main__":
    url = "http://127.0.0.1:8000"
    print(f"Server running at: {url}")
    webbrowser.open(url)

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )