from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BITACORA_FILE = "bitacora.xlsx"
HOJA = "concentrado1"

DIAS = {
    "lunes": (4, 8),
    "martes": (9, 13),
    "miercoles": (14, 18),
    "jueves": (19, 23),
    "viernes": (24, 28),
}

HORAS = ["7:00", "8:00", "9:00", "10:00", "11:00"]


def buscar_profesor(matricula: str, dia: str):
    df = pd.read_excel(BITACORA_FILE, sheet_name=HOJA, header=None)

    dia = dia.lower()
    if dia not in DIAS:
        return None

    col_inicio, col_fin = DIAS[dia]

    # Empieza desde la fila donde están los datos reales
    for fila in range(5, len(df)):
        aula = df.iloc[fila, 0]     # 👈 SALÓN REAL
        grupo = df.iloc[fila, 1]

        for i, col in enumerate(range(col_inicio, col_fin + 1)):
            celda = str(df.iloc[fila, col])

            if matricula == celda:
                return {
                    "dia": dia.capitalize(),
                    "hora": HORAS[i],
                    "aula": aula,
                    "grupo": grupo
                }

    return None


@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resultado": None}
    )


@app.post("/buscar", response_class=HTMLResponse)
def buscar(request: Request, matricula: str = Form(...), dia: str = Form(...)):
    resultado = buscar_profesor(matricula, dia)

    if not resultado:
        mensaje = f"No se encontró al maestro {matricula} el {dia}."
    else:
        mensaje = (
            f"El maestro {matricula} el {resultado['dia']} "
            f"está en el salón {resultado['aula']} "
            f"a las {resultado['hora']} "
            f"(Grupo {resultado['grupo']})"
        )

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resultado": mensaje}
    )
