from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()

# 🔹 Static (para logo, css, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

BITACORA_FILE = "bitacora.xlsx"
HOJA = "concentrado"


def buscar_profesor(matricula, dia):
    df = pd.read_excel(BITACORA_FILE, sheet_name=HOJA, header=None)

    resultados = []

    for fila in range(3, len(df)):
        aula = str(df.iloc[fila, 0]).strip()
        if aula == "nan":
            continue

        for col in range(1, len(df.columns)):
            texto = str(df.iloc[fila, col]).upper()

            if matricula.upper() in texto and dia.upper() in texto:
                resultados.append({
                    "Hora": df.iloc[1, col],
                    "Aula": aula,
                    "Grupo": df.iloc[2, col],
                    "Carrera": df.iloc[0, col]
                })

    return resultados


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "resultado": None
    })


@app.post("/buscar", response_class=HTMLResponse)
def buscar(request: Request,
           matricula: str = Form(...),
           dia: str = Form(...)):

    resultado = buscar_profesor(matricula, dia)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "resultado": resultado
    })
