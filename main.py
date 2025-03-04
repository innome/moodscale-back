from time import time
from fastapi import FastAPI, __version__
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from extra import router as extra_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(extra_router)

origins = [
    "http://127.0.0.1:5173",  # Ajusta al puerto de tu frontend (Vite)
    "http://localhost:5173",
    "https://moodscale-front.vercel.app"  # Ajusta si usas localhost
    # Agrega aquí otras URL permitidas si tienes un dominio
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # or ["*"] para permitir a cualquiera (no recomendable en producción)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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