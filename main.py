from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

BITACORA_FILE = "bitacora.xlsx"
HOJA = "concentrado diur."

DIAS = {
    "lunes": (4, 8),
    "martes": (9, 13),
    "miercoles": (14, 18),
    "jueves": (19, 23),
    "viernes": (24, 28),
}

HORAS = ["7:00", "8:00", "9:00", "10:00", "11:00"]


def normalizar(valor):
    return str(valor).strip().upper()


def buscar_profesor(matricula: str, dia: str):
    df = pd.read_excel(BITACORA_FILE, sheet_name=HOJA, header=None)

    matricula = normalizar(matricula)
    dia = dia.lower()

    if dia not in DIAS:
        return []

    col_inicio, col_fin = DIAS[dia]
    resultados = []

    for fila in range(5, len(df)):
        aula = normalizar(df.iloc[fila, 0])
        grupo = normalizar(df.iloc[fila, 1])

        for i, col in enumerate(range(col_inicio, col_fin + 1)):
            celda = normalizar(df.iloc[fila, col])

            if celda == matricula:
                resultados.append({
                    "hora": HORAS[i],
                    "aula": aula,
                    "grupo": grupo
                })

    return resultados


@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resultados": None}
    )


@app.post("/buscar", response_class=HTMLResponse)
def buscar(request: Request, matricula: str = Form(...), dia: str = Form(...)):
    clases = buscar_profesor(matricula, dia)

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "matricula": matricula.upper(),
            "dia": dia.capitalize(),
            "resultados": clases
        }
    )
