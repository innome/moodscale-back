from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import datetime
import json
import os
from fastapi.middleware.cors import CORSMiddleware
import datetime
from mangum import Mangum

app = FastAPI()

# Archivo de almacenamiento
DATA_FILE = "emotions_log.json"
handler = Mangum(app)

origins = [
    "http://127.0.0.1:5173",  # Ajusta al puerto de tu frontend (Vite)
    "http://localhost:5173",  # Ajusta si usas localhost
    # Agrega aquí otras URL permitidas si tienes un dominio
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # or ["*"] para permitir a cualquiera (no recomendable en producción)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




def default_converter(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4, default=default_converter)

# Cargar datos previos si existen
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            print("Error: El archivo JSON está corrupto o malformado. Se inicializará vacío.")
            return []
    return []

# Guardar datos en archivo
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

emotions_log = load_data()

# Base de datos de preguntas por emoción (más extensa)
questions_db = {
    "tristeza": [
        {
            "question": "¿Te sientes así desde hace mucho?",
            "options": {"No": 1, "Poco tiempo": 2, "Sí, bastante": 4, "Siempre": 5}
        },
        {
            "question": "¿Cómo describirías tu estado de ánimo?",
            "options": {
                "Leve nostalgia": 2,
                "Tristeza moderada": 3,
                "Tristeza profunda": 5
            }
        }
    ],
    "felicidad": [
        {
            "question": "¿Qué generó esta emoción?",
            "options": {
                "Un logro": 3,
                "Alguien especial": 4,
                "Un evento inesperado": 2,
                "Nada en especial": 1
            }
        },
        {
            "question": "¿Compartiste tu alegría con alguien?",
            "options": {
                "Sí": 4,
                "No": 1
            }
        }
    ],
    "frustración": [
        {
            "question": "¿Qué situación te frustró?",
            "options": {"Trabajo": 4, "Estudio": 3, "Familia": 2, "Otro": 1}
        },
        {
            "question": "¿Qué tan difícil te resultó manejarla?",
            "options": {
                "Fácil de sobrellevar": 1,
                "Algo molesto": 2,
                "Muy complejo": 4,
                "Me superó": 5
            }
        }
    ],
    "ansiedad": [
        {
            "question": "¿Sientes síntomas físicos como palpitaciones o sudoración?",
            "options": {"Nunca": 0, "A veces": 2, "Frecuentemente": 4, "Siempre": 5}
        },
        {
            "question": "¿Te resulta difícil concentrarte?",
            "options": {"No": 1, "Un poco": 2, "Mucho": 4}
        }
    ],
    "ira": [
        {
            "question": "¿Expresaste tu enojo de forma impulsiva?",
            "options": {"No": 1, "Un poco": 2, "Sí": 4, "Muy impulsivamente": 5}
        },
        {
            "question": "¿Te resultó difícil calmarte?",
            "options": {"No": 1, "Algo": 3, "Bastante": 5}
        }
    ],
    "miedo": [
        {
            "question": "¿Con qué frecuencia sientes temor?",
            "options": {"Casi nunca": 1, "A veces": 2, "A menudo": 4, "Siempre": 5}
        },
        {
            "question": "¿Intentas evitar situaciones que te asustan?",
            "options": {"No": 0, "Algunas veces": 2, "Frecuentemente": 4, "Siempre": 5}
        }
    ],
    "amor": [
        {
            "question": "¿Qué tan cercana te sientes a la otra persona?",
            "options": {"Poco": 1, "Moderado": 3, "Bastante": 4, "Muchísimo": 5}
        },
        {
            "question": "¿Expresas tu amor con facilidad?",
            "options": {"Rara vez": 1, "A veces": 2, "Casi siempre": 4, "Siempre": 5}
        }
    ],
    "culpa": [
        {
            "question": "¿Sientes que hiciste algo mal?",
            "options": {"No": 1, "Dudoso": 2, "Un error importante": 4, "Muy grave": 5}
        },
        {
            "question": "¿Has intentado reparar el daño?",
            "options": {"No": 1, "Parcialmente": 3, "Sí": 5}
        }
    ],
    "sorpresa": [
        {
            "question": "¿El evento fue inesperado?",
            "options": {"Leve sorpresa": 2, "Moderado": 3, "Muy sorprendente": 5}
        },
        {
            "question": "¿Fue una sorpresa agradable?",
            "options": {"No": 1, "Algo": 3, "Sí": 5}
        }
    ]
}


class EmotionEntry(BaseModel):
    emotion: str
    intensity: int
    responses: Dict[str, int]
    date: str  # en vez de datetime.date
    note: Optional[str] = None  # Campo opcional para la nota

@app.post("/log_emotion/")
def log_emotion(entry: EmotionEntry):
    if entry.emotion not in questions_db:
        raise HTTPException(status_code=400, detail="Emoción no válida")

    # Convertir la fecha a string para evitar error "Object of type date is not JSON serializable"
    entry_data = entry.dict()
    entry_data["date"] = str(entry_data["date"])

    # Guardar en la lista en memoria
    emotions_log.append(entry_data)
    # Guardar en archivo JSON
    save_data(emotions_log)
    return {"message": "Emoción registrada exitosamente"}

@app.get("/questions/{emotion}")
def get_questions(emotion: str):
    if emotion not in questions_db:
        raise HTTPException(status_code=404, detail="No hay preguntas para esta emoción")
    return questions_db[emotion]

@app.get("/stats/")
def get_stats():
    if not emotions_log:
        return {
            "overall": {},
            "by_question": {}
        }

    stats = {}
    question_stats = {}

    for entry in emotions_log:
        emotion = entry["emotion"]
        intensity = entry["intensity"]
        responses = entry["responses"]

        if emotion not in stats:
            stats[emotion] = []
        stats[emotion].append(intensity)

        if emotion not in question_stats:
            question_stats[emotion] = {}
        for q_idx, q_value in responses.items():
            if q_idx not in question_stats[emotion]:
                question_stats[emotion][q_idx] = []
            question_stats[emotion][q_idx].append(q_value)

    avg_stats = {
        emotion: sum(values) / len(values) for emotion, values in stats.items()
    }

    avg_question_stats = {}
    for emotion, q_dict in question_stats.items():
        avg_question_stats[emotion] = {}
        for q_idx, q_values in q_dict.items():
            avg_question_stats[emotion][q_idx] = sum(q_values) / len(q_values)

    return {
        "overall": avg_stats,
        "by_question": avg_question_stats
    }

@app.get("/entries/")
def get_entries():
    return emotions_log

@app.get("/")
def main():
    return "Microservicios Funcionando"