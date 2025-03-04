from time import time
from fastapi import FastAPI, __version__, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from extra import router as extra_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://moodscale-front.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{full_path:path}")
async def preflight_handler(request: Request, full_path: str):
    return Response(headers={
        "Access-Control-Allow-Origin": "https://moodscale-front.vercel.app",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    })

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"Access-Control-Allow-Origin": "https://moodscale-front.vercel.app"}
    )

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(extra_router)


html = f"""
<!DOCTYPE html>
<html>
    <head>
        <title>FastAPI on Vercel</title>
        <link rel="icon" href="/static/favicon.ico" type="image/x-icon" />
    </head>
    <body>
        <div class="bg-gray-200 p-4 rounded-lg shadow-lg">
            <h1>Hello from FastAPI@{__version__}</h1>
            <ul>
                <li><a href="/docs">/docs</a></li>
                <li><a href="/redoc">/redoc</a></li>
            </ul>
            <p>Powered by <a href="https://vercel.com" target="_blank">Vercel</a></p>
        </div>
    </body>
</html>
"""

@app.get("/")
async def root():
    return HTMLResponse(html)

@app.get('/ping')
async def hello():
    return {'res': 'pong', 'version': __version__, "time": time()}