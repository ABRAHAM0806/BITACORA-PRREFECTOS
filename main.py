from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BITACORA_FILE = "bitacora.xlsx"
DIAS = ["lunes", "martes", "miércoles", "miercoles", "jueves", "viernes"]

def buscar_profesor(matricula, dia):
    xls = pd.ExcelFile(BITACORA_FILE)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=None)

        for fila_idx, fila in df.iterrows():
            for col_idx, valor in fila.items():
                if str(valor).strip() == str(matricula):
                    dia = dia.lower()

                    # Buscar encabezado del día hacia arriba
                    for offset in range(1, 5):
                        encabezado = df.iloc[fila_idx - offset, col_idx]
                        if encabezado and str(encabezado).lower() in DIAS:
                            hora = df.iloc[fila_idx - offset + 1, col_idx]
                            aula = df.iloc[fila_idx, col_idx + 1]

                            return {
                                "hoja": sheet,
                                "dia": encabezado,
                                "hora": hora,
                                "aula": aula
                            }
    return None

@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resultado": None}
    )

@app.post("/buscar", response_class=HTMLResponse)
def buscar(
    request: Request,
    matricula: str = Form(...),
    dia: str = Form(...)
):
    resultado = buscar_profesor(matricula, dia)

    if not resultado:
        mensaje = f"No se encontró al maestro {matricula} el {dia}."
    else:
        mensaje = (
            f"El maestro {matricula} el {resultado['dia']} "
            f"está en el aula {resultado['aula']} "
            f"en horario {resultado['hora']}."
        )

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resultado": mensaje}
    )

