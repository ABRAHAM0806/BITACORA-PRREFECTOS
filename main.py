from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BITACORA_FILE = "bitacora.xlsx"
DIAS = ["lunes", "martes", "miércoles", "miercoles", "jueves", "viernes", "sabado"]

# ---------- UTILIDADES ----------

def es_aula(valor, matricula):
    if valor is None:
        return False

    texto = str(valor).strip()

    # No confundir aula con matrícula
    if texto == str(matricula):
        return False

    patrones = [
        r"^[A-Z]\d{3}$",   # A229, B203
        r"^\d{3,4}$"       # 1517, 201
    ]

    return any(re.match(p, texto) for p in patrones)

def buscar_profesor(matricula, dia_buscado):
    dia_buscado = dia_buscado.lower().strip()
    xls = pd.ExcelFile(BITACORA_FILE)

    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, header=None)

        for fila_idx in range(len(df)):
            for col_idx in range(len(df.columns)):
                valor = df.iat[fila_idx, col_idx]

                if str(valor).strip() == str(matricula):

                    # 🔎 Buscar día hacia arriba
                    dia_encontrado = None
                    hora = None
                    for offset in range(1, 7):
                        if fila_idx - offset >= 0:
                            posible_dia = str(df.iat[fila_idx - offset, col_idx]).lower()
                            if posible_dia in DIAS and posible_dia == dia_buscado:
                                dia_encontrado = posible_dia.capitalize()
                                hora = df.iat[fila_idx - offset + 1, col_idx]
                                break

                    if not dia_encontrado:
                        continue

                    # 🔎 Buscar aula alrededor
                    aula = None
                    for r in range(fila_idx - 1, fila_idx + 2):
                        for c in range(col_idx - 2, col_idx + 3):
                            if 0 <= r < len(df) and 0 <= c < len(df.columns):
                                posible = df.iat[r, c]
                                if es_aula(posible, matricula):
                                    aula = posible
                                    break
                        if aula:
                            break

                    return {
                        "matricula": matricula,
                        "dia": dia_encontrado,
                        "hora": hora,
                        "aula": aula,
                        "hoja": sheet
                    }

    return None

# ---------- RUTAS ----------

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
            f"El maestro {resultado['matricula']} el {resultado['dia']} "
            f"está en el aula {resultado['aula']} "
            f"en horario {resultado['hora']}."
        )

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "resultado": mensaje}
    )

