from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ===============================
# ARCHIVOS
# ===============================
ARCHIVOS = [
    {
        "file": "bitacora.xlsx",
        "sheet": "concentrado",
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
        "file": "bitacora 2.xlsx",
        "sheet": "diur2",
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

# ⏰ TODAS las horas (mañana + tarde)
HORAS = [
    "7:00", "8:00", "9:00", "10:00", "11:00",
    "12:00", "13:00", "14:00"
]

# ===============================
def normalizar(valor):
    return str(valor).strip().upper()


# ===============================
# ORDENAR POR HORA (FORMA CORRECTA)
# ===============================
def ordenar_por_hora(resultados):
    def hora_a_minutos(h):
        h, m = h.split(":")
        return int(h) * 60 + int(m)

    return sorted(resultados, key=lambda x: hora_a_minutos(x["hora"]))


# ===============================
def buscar_profesor(matricula: str, dia: str):
    matricula = normalizar(matricula)
    dia = dia.lower()
    resultados = []

    if dia not in DIAS:
        return resultados

    col_inicio, col_fin = DIAS[dia]

    for info in ARCHIVOS:
        try:
            df = pd.read_excel(info["file"], sheet_name=info["sheet"], header=None)
        except Exception as e:
            print(f"Error leyendo {info['file']} - {e}")
            continue

        for fila in range(4, 68):
            aula = normalizar(df.iloc[fila, 0])
            grupo = normalizar(df.iloc[fila, 1])
            licenciatura = str(df.iloc[fila, 2]).strip()

            for i, col in enumerate(range(col_inicio, col_fin + 1)):
                if i >= len(HORAS):
                    continue

                celda = normalizar(df.iloc[fila, col])

                if celda == matricula:
                    resultados.append({
                        "hora": HORAS[i],
                        "aula": aula,
                        "grupo": grupo,
                        "licenciatura": licenciatura
                    })

    # 🔑 ORDEN FINAL (NO sort inline)
    return ordenar_por_hora(resultados)


# ===============================
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




