import os
import json
import gspread
import pandas as pd
import sys

def transferir_datos():
    # URL de origen (Exportación directa a CSV)
    url_origen = "https://docs.google.com/spreadsheets/d/16PzK230jtrjkpHYq5mYSFrdeXk-0B6N7/export?format=csv&gid=305780908"
    
    # URL de destino
    url_destino = "https://docs.google.com/spreadsheets/d/1BhMQsml0BjFiFFKiXiOehaCBRvRYdWbuRZxnnWAdF6Y/edit"
    
    print("1. Descargando datos públicos de la hoja origen...")
    try:
        df = pd.read_csv(url_origen)
        df = df.fillna("")
        print(f"-> Se capturaron {len(df)} filas y {len(df.columns)} columnas.")
    except Exception as e:
        print(f"Error al descargar la hoja de origen: {e}")
        sys.exit(1)

    print("\n2. Autenticando con Google...")
    try:
        # Detecta si estamos en GitHub Actions usando la variable de entorno
        if 'GOOGLE_CREDENTIALS' in os.environ:
            print("-> Usando credenciales ocultas desde GitHub Secrets...")
            creds_json = json.loads(os.environ['GOOGLE_CREDENTIALS'])
            gc = gspread.service_account_from_dict(creds_json)
        else:
            print("-> Usando archivo local credenciales.json...")
            gc = gspread.service_account(filename='credenciales.json')
    except Exception as e:
        print(f"Error de autenticación: {e}")
        sys.exit(1)

    print("\n3. Conectando a la hoja de destino...")
    try:
        documento_destino = gc.open_by_url(url_destino)
        pestaña_destino = documento_destino.sheet1
    except Exception as e:
        print(f"Error al abrir la hoja de destino: {e}")
        sys.exit(1)

    print("\n4. Escribiendo datos en la hoja de destino...")
    try:
        valores_a_subir = [df.columns.values.tolist()] + df.values.tolist()
        pestaña_destino.clear()
        pestaña_destino.update(valores_a_subir)
        print("\n¡Éxito! Los datos han sido transferidos a tu hoja destino.")
    except Exception as e:
        print(f"Error al escribir los datos: {e}")
        sys.exit(1)

if __name__ == "__main__":
    transferir_datos()
