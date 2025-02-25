from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import sqlite3
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import uvicorn
from typing import List

app = FastAPI()

#Ruta csv
csv_path = './data/Advertising.csv'

# Cargar el modelo entrenado al iniciar la app
with open("./ejercicio/data/advertising_model.pkl", "rb") as model_file:
    model = pickle.load(model_file)

# Definir modelo entrada
class Advertising(BaseModel):
    TV: float
    radio: float
    newspaper: float

# Definir modelo salida
class PredictionOutput(BaseModel):
    prediction: float


# 1. Endpoint de predicción
@app.post("/predict", response_model=PredictionOutput)
async def predict(advertising: Advertising):
    try:
        input_data = np.array([[advertising.TV, advertising.radio, advertising.newspaper]])
        prediction = model.predict(input_data)
        return PredictionOutput(prediction=round(prediction, 2))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la predicción: {e}")

# 2. Endpoint de ingesta de datos
@app.post("/ingest")
async def ingest(data: List[Advertising]):
    try:
        # Cargar el archivo CSV en un DataFrame
        df = pd.read_csv(csv_path)
        
        # Agregar los nuevos registros al DataFrame
        new_data = pd.DataFrame([{
            'TV': record.TV,
            'radio': record.radio,
            'newspaper': record.newspaper,
            'sales': None 
        } for record in data])

        # Concatenar nuevos registros con los existentes
        df = pd.concat([df, new_data], ignore_index=True)
        
        # Guardar DataFrame actualizado en el archivo CSV
        df.to_csv(csv_path, index=False)

        return {"message": "Datos ingresados correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al almacenar los datos: {e}")


# 3. Endpoint de reentramiento del modelo
@app.post("/retrain")
async def retrain():
    try:
        # Leer archivo CSV
        df = pd.read_csv(csv_path)

        # Asegurar que no haya valores nulos en las columnas necesarias
        df = df.dropna(subset=['TV', 'radio', 'newspaper', 'sales'])

        # Definir las variables independientes (X) y la variable dependiente (y)
        X = df[['TV', 'radio', 'newspaper']].values
        y = df['sales'].values

        # Reentrenar modelo
        model = LinearRegression()
        model.fit(X, y)

        # Guardar el modelo actualizado
        with open("./ejercicio/data/advertising_model.pkl", "wb") as model_file:
            pickle.dump(model, model_file)

        return {"message": "Modelo reentrenado correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al reentrenar el modelo: {e}")


# Ejecutar la aplicación    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)  