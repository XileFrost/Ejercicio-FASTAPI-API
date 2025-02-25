from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import uvicorn

app = FastAPI()

# Configuración
DATABASE_NAME = "advertising.db"
CSV_PATH = "./data/Advertising.csv"

# Cargar modelo inicial
with open("./data/advertising_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

# Conexión a la base de datos
def get_db():
    return sqlite3.connect(DATABASE_NAME)

# Inicializar base de datos y cargar CSV
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS advertising (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tv REAL NOT NULL,
            radio REAL NOT NULL,
            newspaper REAL NOT NULL,
            sales REAL NOT NULL
        )
    ''')
    
    if cursor.execute("SELECT COUNT(*) FROM advertising").fetchone()[0] == 0:
        df = pd.read_csv(CSV_PATH)
        df['newspaper'] = df['newspaper'].astype(str).str.replace('s', '').astype(float)
        
        df[['tv', 'radio', 'newspaper', 'sales']].to_sql(
            'advertising',
            conn,
            if_exists='append',
            index=False
        )
        conn.commit()
    
    conn.close()

init_db()

# Modelos Pydantic para los tests
class IngestRequest(BaseModel):
    data: list

class PredictRequest(BaseModel):
    data: list

# Endpoints ajustados para los tests
@app.post("/ingest")
async def ingest_data(request: IngestRequest):
    conn = get_db()
    cursor = conn.cursor()
    try:
        for entry in request.data:
            if len(entry) != 4:
                raise HTTPException(status_code=400, detail="Formato de datos incorrecto")
                
            cursor.execute('''
                INSERT INTO advertising (tv, radio, newspaper, sales)
                VALUES (?, ?, ?, ?)
            ''', (entry[0], entry[1], entry[2], entry[3]))
        
        conn.commit()
        return {"message": "Datos ingresados correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/predict")
async def predict(request: PredictRequest):
    try:
        input_data = np.array(request.data).astype(float)
        predictions = model.predict(input_data)
        return {"prediction": [round(float(p), 2) for p in predictions]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/retrain")
async def retrain_model():
    conn = get_db()
    try:
        df = pd.read_sql('SELECT tv, radio, newspaper, sales FROM advertising', conn)
        
        if len(df) < 1:
            return {"message": "No hay datos para reentrenar"}
        
        X = df[['tv', 'radio', 'newspaper']]
        y = df['sales']
        
        new_model = LinearRegression()
        new_model.fit(X, y)
        
        with open("./data/advertising_model.pkl", "wb") as model_file:
            pickle.dump(new_model, model_file)
        
        global model
        model = new_model
        
        return {"message": "Modelo reentrenado correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

# Ejecutar la aplicación    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)  