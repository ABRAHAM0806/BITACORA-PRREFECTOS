from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()

templates = Jinja2Templates(directory="templates")

ARCHIVO = "bitacora 2.xlsx"
HOJA = "diur2"


def ordenar_hora(h):
    """
    Convierte '07:00-08:00' → 700 para poder ordenar bien
    """
    try:
        return int(h.split(":")[0]) * 100
    except:
        return 9999


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resultados": None}
    )


@app.post("/buscar", response_class=HTMLResponse)
async def buscar(
    request: Request,
    matricula: str = Form(...)
):
    try:
        df = pd.read_excel(ARCHIVO, sheet_name=HOJA)
    except Exception as e:
        print(f"Error leyendo {ARCHIVO} - {e}")
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "resultados": []}
        )

    # Normalizamos columnas (MUY IMPORTANTE)
    df.columns = df.columns.str.strip().str.upper()

    # Ajusta aquí si tus columnas se llaman diferente
    COL_MATRICULA = "MATRICULA"
    COL_HORA = "HORA"
    COL_AULA = "AULA"
    COL_GRUPO = "GRUPO"
    COL_LIC = "LICENCIATURA"

    if COL_MATRICULA not in df.columns:
        print("No existe la columna MATRICULA")
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "resultados": []}
        )

    # Filtrar por matrícula
    df_filtrado = df[df[COL_MATRICULA].astype(str) == matricula.strip()]

    if df_filtrado.empty:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "resultados": []}
        )

    # Ordenar horarios correctamente
    df_filtrado["__orden"] = df_filtrado[COL_HORA].astype(str).apply(ordenar_hora)
    df_filtrado = df_filtrado.sort_values("__orden")

    resultados = []

    for _, fila in df_filtrado.iterrows():
        resultados.append({
            "hora": str(fila.get(COL_HORA, "")),
            "aula": str(fila.get(COL_AULA, "")),
            "grupo": str(fila.get(COL_GRUPO, "")),
            "licenciatura": str(fila.get(COL_LIC, ""))
        })

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "resultados": resultados
        }
    )





