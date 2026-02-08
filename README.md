# API_MODELO

API desarrollada con **FastAPI** para servir un modelo de predicción de consumo energético.
El modelo se carga desde **Databricks Model Registry (MLflow)** y expone un endpoint para obtener predicciones en kWh.

---

## Instalación

Clonar repositorio e instalar dependencias:

```bash
git clone <URL_DEL_REPO>
cd API_MODELO
pip install -r requirements.txt
```

---

## Variables de entorno

La API requiere acceso a Databricks para cargar el modelo.
Crear un archivo `.env` en la raíz del proyecto:

```
DATABRICKS_HOST=<tu_host_databricks>
DATABRICKS_TOKEN=<tu_token_databricks>
```

---

## Ejecución

Lanzar la API:

```bash
uvicorn main:app --reload
```

(Asumiendo que el archivo se llama `main.py`)

La documentación interactiva estará disponible en:

```
http://127.0.0.1:8000/docs
```

---

## Funcionamiento

Al arrancar:

1. Se cargan variables de entorno
2. Se conecta a MLflow en Databricks
3. Se descarga el modelo registrado:

```
models:/workspace.default.consumo_tenerife/1
```

4. Se mantiene en memoria para servir predicciones

---

## Endpoint principal

### POST `/predict`

Devuelve predicción de consumo energético.

#### Request JSON

```json
{
  "dia": 15,
  "mes": 6,
  "cups_municipio": "ADEJE",
  "cups_distribuidor": "EDISTRIBUCIÓN"
}
```

#### Response

```json
{
  "prediccion_kWh": 123
}
```

---

## Health check

### GET `/health`

Permite verificar si el modelo está cargado:

```
{"status": "ok"}
```

o

```
{"status": "ko"}
```

---

## Estructura

```
.
├── main.py
├── requirements.txt
├── .env
└── README.md
```

---

## Dependencias principales

* fastapi
* uvicorn
* pydantic
* mlflow
* databricks-sdk
* pandas
* numpy
* python-dotenv
* scikit-learn
* cloudpickle

---

