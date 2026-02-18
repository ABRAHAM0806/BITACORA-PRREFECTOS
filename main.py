from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BITACORA_FILE = "bitacora.xlsx"

def cargar_bitacora():
    return pd.read_excel(BITACORA_FILE, sheet_name="concentrado diur.")

@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "resultado": None})

@app.post("/buscar", response_class=HTMLResponse)
def buscar(request: Request, matricula: int = Form(...), dia: str = Form(...)):
    df = cargar_bitacora()
    resultado = df[
        (df["Matricula"] == matricula) &
        (df["Dia"].str.lower() == dia.lower())
    ]

    if resultado.empty:
        mensaje = f"El maestro {matricula} no tiene clase asignada el {dia}."
    else:
        aula = resultado["Aula"].values[0]
        hora = resultado["Hora"].values[0]
        mensaje = f"El maestro {matricula} el {dia} está en el aula {aula} de {hora}."

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resultado": mensaje}
    )
