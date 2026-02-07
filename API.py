from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import mlflow
import mlflow.pyfunc

import pandas as pd
import numpy as np
import os

# ⭐ NUEVO — cargar .env local
from dotenv import load_dotenv
load_dotenv()


# ⭐ Configurar credenciales Databricks
os.environ["DATABRICKS_HOST"] = os.getenv("DATABRICKS_HOST")
os.environ["DATABRICKS_TOKEN"] = os.getenv("DATABRICKS_TOKEN")

# ⭐ Decirle a MLflow que use Databricks
mlflow.set_tracking_uri("databricks")

# ⭐ URL del modelo (CAMBIA ESTO)
URL_MODELO = "models:/ÁrbolDecisión/1"
# o
# URL_MODELO = "models:/consumo_model/1"


@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        # ⭐ usar pyfunc (más robusto en deploy)
        app.state.modelo = mlflow.pyfunc.load_model(URL_MODELO)
        print("Modelo cargado desde Databricks")

    except Exception as e:
        print("Error cargando modelo:", e)
        app.state.modelo = None

    yield
    print("Aplicación detenida")


app = FastAPI(
    title="API Consumo Energético",
    lifespan=lifespan
)


class PredictRequest(BaseModel):
    dia: int
    mes: int
    cups_municipio: str
    cups_distribuidor: str


@app.post("/predict")
def predict(data: PredictRequest):

    if app.state.modelo is None:
        raise HTTPException(status_code=500, detail="Modelo no cargado")

    X = pd.DataFrame([{
        "dia": data.dia,
        "mes": data.mes,
        "cups_municipio": data.cups_municipio,
        "cups_distribuidor": data.cups_distribuidor
    }])

    pred_log = app.state.modelo.predict(X)[0]
    pred_kwh = int(np.expm1(pred_log))

    return {"prediccion_kWh": pred_kwh}

