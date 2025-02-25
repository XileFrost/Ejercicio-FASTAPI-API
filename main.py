from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import uvicorn

app = FastAPI()

DATABASE_NAME = "advertising.db"
CSV_PATH = "/app/data/Advertising.csv"

def get_db():
    return sqlite3.connect(DATABASE_NAME)

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS advertising (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            TV REAL NOT NULL,
            radio REAL NOT NULL,
            newspaper REAL NOT NULL,
            sales REAL NOT NULL
        )
    ''')
    
    if cursor.execute("SELECT COUNT(*) FROM advertising").fetchone()[0] == 0:
        df = pd.read_csv(CSV_PATH)
        df = df.rename(columns={'newpaper': 'newspaper'})
        df['newspaper'] = df['newspaper'].astype(str).str.replace('s', '').astype(float)
        df[['TV', 'radio', 'newspaper', 'sales']].to_sql(
            'advertising',
            conn,
            if_exists='append',
            index=False
        )
        conn.commit()
    
    conn.close()

init_db()

class PredictionInput(BaseModel):
    TV: float
    radio: float
    newspaper: float

class TrainingData(BaseModel):
    TV: float
    radio: float
    newspaper: float
    sales: float

@app.post("/predict")
async def predict(data: PredictionInput):
    try:
        input_data = np.array([[data.TV, data.radio, data.newspaper]])
        prediction = model.predict(input_data)
        return {"prediction": round(float(prediction[0]), 2}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
async def ingest_data(data: TrainingData):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO advertising (TV, radio, newspaper, sales)
            VALUES (?, ?, ?, ?)
        ''', (data.TV, data.radio, data.newspaper, data.sales))
        conn.commit()
        return {"message": "Datos ingresados correctamente"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/retrain")
async def retrain_model():
    conn = get_db()
    try:
        df = pd.read_sql('SELECT TV, radio, newspaper, sales FROM advertising', conn)
        X = df[['TV', 'radio', 'newspaper']]
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)