import zipfile
import pandas as pd
import os

def procesar_base_mesas(archivo_zip, tipo):
    print(f'Procesando {tipo} desde {archivo_zip}...')
    
    with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
        archivos = zip_ref.namelist()
        archivo_csv = archivos[0]
        print(f'  Archivo encontrado: {archivo_csv}')
        
        with zip_ref.open(archivo_csv) as f:
            encodings = ['utf-8', 'latin1', 'cp1252']
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(f, encoding=encoding)
                    print(f'  Encoding exitoso: {encoding}')
                    break
                except UnicodeDecodeError:
                    continue
            
            if df is None:
                raise ValueError(f'No se pudo leer el archivo {archivo_csv}')
    
    print(f'  Total de electores en {tipo}: {len(df):,}')
    
    df_agrupado = df.groupby(['cod_circ', 'nro_mesa']).agg({
        'distrito': 'first',
        'establecimiento': 'first',
        'id_persona': 'count'
    }).reset_index()
    
    df_agrupado = df_agrupado.rename(columns={'id_persona': 'cantidad_electores'})
    df_agrupado['tipo'] = tipo
    
    columnas_finales = ['cod_circ', 'distrito', 'establecimiento', 'nro_mesa', 'cantidad_electores', 'tipo']
    df_agrupado = df_agrupado[columnas_finales]
    
    return df_agrupado

print('=== CREANDO NUEVA BASE DE DATOS DE MESAS ===')

archivo_nativos = 'utils/data/padron_2025.zip'
archivo_extranjeros = 'utils/data/padron_extranjeros_2025.zip'

df_nativos = procesar_base_mesas(archivo_nativos, 'NATIVA')
df_extranjeros = procesar_base_mesas(archivo_extranjeros, 'EXTRANJERA')

df_final = pd.concat([df_nativos, df_extranjeros], ignore_index=True)

archivo_salida = 'base_mesas_electores.csv'
df_final.to_csv(archivo_salida, index=False, encoding='utf-8')