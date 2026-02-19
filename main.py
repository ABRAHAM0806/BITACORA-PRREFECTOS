from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BITACORA_FILE = "bitacora.xlsx"
HOJA = "concentrado"

DIAS = ["lunes", "martes", "miércoles", "miercoles", "jueves", "viernes", "sabado"]

# ---------- LOGICA PRINCIPAL ----------

def buscar_profesor(matricula, dia_buscado):
    dia_buscado = dia_buscado.lower().strip()

    df = pd.read_excel(
        BITACORA_FILE,
        sheet_name=HOJA,
        header=None
    )

    # Aulas están en columna A (index 0), filas 4 a 68
    for fila in range(3, 68):  # A4 = index 3
        aula = df.iat[fila, 0]

        if pd.isna(aula):
            continue

        # Revisar columnas de horarios (desde columna B en adelante)
        for col in range(1, len(df.columns)):
            valor = df.iat[fila, col]

            if str(valor).strip() == str(matricula):

                # Buscar día en el encabezado (filas superiores)
                for encabezado_fila in range(0, 3):
                    encabezado = str(df.iat[encabezado_fila, col]).lower()

                    if encabezado in DIAS and encabezado == dia_buscado:
                        # Hora normalmente está justo debajo del día
                        hora = df.iat[encabezado_fila + 1, col]

                        return {
                            "matricula": matricula,
                            "dia": encabezado.capitalize(),
                            "aula": aula,
                            "hora": hora
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

