from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ===============================
# CONFIGURACIÓN DE ARCHIVOS
# ===============================
ARCHIVOS = [
    {
        "archivo": "bitacora.xlsx",
        "hoja": "concentrado diur.",
        "horas": ["7:00", "8:00", "9:00", "10:00", "11:00"],
        "dias": {
            "lunes": (4, 8),
            "martes": (9, 13),
            "miercoles": (14, 18),
            "jueves": (19, 23),
            "viernes": (24, 28),
        }
    },
    {
        "archivo": "bitacora 2.xlsx",
        "hoja": "concentrado diur2.",
        "horas": ["12:00", "13:00", "14:00"],
        "dias": {
            "lunes": (4, 6),
            "martes": (7, 9),
            "miercoles": (10, 12),
            "jueves": (13, 15),
            "viernes": (16, 18),
        }
    }
]

# ===============================
def normalizar(valor):
    return str(valor).strip().upper()

# ===============================
def buscar_en_archivo(matricula, dia, config):
    resultados = []

    try:
        df = pd.read_excel(
            config["archivo"],
            sheet_name=config["hoja"],
            header=None
        )
    except Exception as e:
        # SI ESTE ARCHIVO FALLA, NO ROMPE TODO
        print(f"Error leyendo {config['archivo']} - {e}")
        return []

    col_inicio, col_fin = config["dias"][dia]
    horas = config["horas"]

    for fila in range(5, len(df)):
        aula = normalizar(df.iloc[fila, 0])
        grupo = normalizar(df.iloc[fila, 1])

        for i, col in enumerate(range(col_inicio, col_fin + 1)):
            if col >= df.shape[1] or i >= len(horas):
                continue

            celda = normalizar(df.iloc[fila, col])

            if celda == matricula:
                resultados.append({
                    "hora": horas[i],
                    "aula": aula,
                    "grupo": grupo
                })

    return resultados

# ===============================
def buscar_profesor(matricula, dia):
    matricula = normalizar(matricula)
    dia = dia.lower()
    resultados = []

    for config in ARCHIVOS:
        if dia in config["dias"]:
            resultados.extend(buscar_en_archivo(matricula, dia, config))

    resultados.sort(key=lambda x: x["hora"])
    return resultados

# ===============================
@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resultados": None}
    )

# ===============================
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



