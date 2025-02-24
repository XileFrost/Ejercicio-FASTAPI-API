# Ejercicio-FASTAPI-API
Ejercicio clase lunes 24 febrero 2025

**Se presenta el siguiente caso de uso**

Una empresa distribuidora de ámbito nacional pretende utilizar un modelo desarrollado por el departamento de data science, con el que consiguen una predicción de las ventas a partir de los gastos en marketing de anuncios en televisión, radio y periódicos. Quieren incorporar estos datos dentro de su página web interna, donde comparten todo tipo de información relativa a resultados de la empresa, ventas, adquisiciones, etc... La web está desarrollada en AngularJS, mientras que el modelo se desarrolló en Python, por lo que precisamos de una interfaz de comunicación entre ambos sistemas.

El equipo de desarrollo necesita que implementes un microservicio para que ellos puedan consumir el modelo desde la propia web, comunicándose con una BBDD para ingestar o reentrenar el modelo. No vale base de datos en csv. El microservicio tiene que cumplir las siguientes características:
1. Ofrezca la predicción de ventas a partir de todos los valores de gastos en publicidad. (/predict)
2. Un endpoint para almacenar nuevos registros en la base de datos que deberás crear previamente.(/ingest)
3. Posibilidad de reentrenar de nuevo el modelo con los posibles nuevos registros que se recojan. (/retrain)


**NOTAS**: 
1. Deberás desplegarlo desde un repositorio de github.
2. Ojo con la ruta para hacer el load de tu modelo y datos, comprueba cual es la ruta en la que está buscándolo.
3. El desarrollo de un modelo de machine learning no es el objetivo del ejercicio, sino el desarrollo de una API con FastAPI.
4. Deberán pasar los tests para verificar que funcionan correctamente con pytest test_api.py desde terminal.

**Entregable**: repositorio github.
