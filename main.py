from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BITACORA_FILE = "bitacora.xlsx"
HOJA = "concentrado diur."  # así se llama tu hoja ahora

def buscar_profesor(matricula, dia):
    df = pd.read_excel(
        BITACORA_FILE,
        sheet_name=HOJA,
        header=None
    )

    resultados = []

    # FILAS donde empiezan los datos reales
    for fila in range(3, len(df)):
        aula = str(df.iloc[fila, 0]).strip()
        if aula == "nan":
            continue

        for col in range(1, len(df.columns)):
            valor = str(df.iloc[fila, col]).strip()

            if matricula.upper() in valor.upper() and dia.upper() in valor.upper():
                # FILAS FIJAS POR TU FORMATO
                hora = df.iloc[1, col]
                grupo = df.iloc[2, col]
                carrera = df.iloc[0, col]

                resultados.append({
                    "Hora": hora,
                    "Aula": aula,
                    "Grupo": grupo,
                    "Carrera": carrera
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
