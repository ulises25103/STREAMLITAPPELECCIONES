import pandas as pd
import os
from pathlib import Path

def analizar_diferencias_union():
    """
    Analiza por qué no hay coincidencias en la unión de extranjeros con mesas.
    """

    # Cambiar al directorio del proyecto
    os.chdir(Path(__file__).parent)

    print("🔍 Analizando diferencias en la unión de datos...")

    # Rutas de archivos
    ruta_extranjeros = "utils/data/padron_extranjeros_2025.csv"
    ruta_mesas = "utils/data/mesas_electores_reducido.csv"

    # Cargar datos
    print("📖 Cargando datos...")
    df_extranjeros = pd.read_csv(ruta_extranjeros, encoding='utf-8')
    df_mesas = pd.read_csv(ruta_mesas, encoding='utf-8')

    # Columnas de agrupación
    columnas_clave = ['nombre_distrito', 'cod_circ', 'nro_mesa', 'establecimiento']

    print("\n📊 Análisis de coincidencias por columna:")

    # Analizar cada columna por separado
    for col in columnas_clave:
        if col in df_extranjeros.columns and col in df_mesas.columns:
            valores_extranjeros = set(df_extranjeros[col].unique())
            valores_mesas = set(df_mesas[col].unique())

            coincidencias = valores_extranjeros.intersection(valores_mesas)
            solo_extranjeros = valores_extranjeros - valores_mesas
            solo_mesas = valores_mesas - valores_extranjeros

            print(f"\n🔹 Columna: {col}")
            print(f"   - Coincidencias: {len(coincidencias):,}")
            print(f"   - Solo en extranjeros: {len(solo_extranjeros):,}")
            print(f"   - Solo en mesas: {len(solo_mesas):,}")

            if len(solo_extranjeros) > 0:
                print(f"   - Ejemplos solo en extranjeros: {list(solo_extranjeros)[:3]}")
            if len(solo_mesas) > 0:
                print(f"   - Ejemplos solo en mesas: {list(solo_mesas)[:3]}")

    # Crear claves compuestas para análisis más detallado
    print("\n🔗 Análisis de claves compuestas:")

    # Crear clave compuesta
    df_extranjeros['clave_union'] = df_extranjeros[columnas_clave].astype(str).agg('-'.join, axis=1)
    df_mesas['clave_union'] = df_mesas[columnas_clave].astype(str).agg('-'.join, axis=1)

    claves_extranjeros = set(df_extranjeros['clave_union'].unique())
    claves_mesas = set(df_mesas['clave_union'].unique())

    coincidencias_claves = claves_extranjeros.intersection(claves_mesas)
    solo_extranjeros_claves = claves_extranjeros - claves_mesas

    print(f"   - Claves totales en extranjeros: {len(claves_extranjeros):,}")
    print(f"   - Claves totales en mesas: {len(claves_mesas):,}")
    print(f"   - Claves coincidentes: {len(coincidencias_claves):,}")
    print(f"   - Claves solo en extranjeros: {len(solo_extranjeros_claves):,}")

    if len(solo_extranjeros_claves) > 0:
        print("
🔍 Ejemplos de claves solo en extranjeros:"        for clave in list(solo_extranjeros_claves)[:5]:
            partes = clave.split('-')
            print(f"   - Distrito: {partes[0]}, Circuito: {partes[1]}, Mesa: {partes[2]}")
            print(f"     Establecimiento: {partes[3]}")

    # Buscar posibles coincidencias aproximadas en establecimientos
    print("
🔍 Analizando establecimientos que podrían coincidir..."    establecimientos_extranjeros = set(df_extranjeros['establecimiento'].unique())
    establecimientos_mesas = set(df_mesas['establecimiento'].unique())

    # Buscar establecimientos similares
    posibles_coincidencias = []
    for est_ext in establecimientos_extranjeros:
        for est_mesa in establecimientos_mesas:
            if est_ext.lower().strip() == est_mesa.lower().strip():
                posibles_coincidencias.append((est_ext, est_mesa))
                break

    if posibles_coincidencias:
        print(f"✅ Encontradas {len(posibles_coincidencias)} coincidencias exactas de establecimientos")
        for ext, mesa in posibles_coincidencias[:3]:
            print(f"   - '{ext}' ↔ '{mesa}'")
    else:
        print("❌ No se encontraron coincidencias exactas de establecimientos")

    # Análisis de distritos
    print("
🏛️ Análisis de distritos:"    distritos_extranjeros = sorted(df_extranjeros['nombre_distrito'].unique())
    distritos_mesas = sorted(df_mesas['nombre_distrito'].unique())

    print(f"   - Distritos en extranjeros: {len(distritos_extranjeros)}")
    print(f"   - Distritos en mesas: {len(distritos_mesas)}")

    # Comparar distritos
    distritos_comunes = set(distritos_extranjeros).intersection(set(distritos_mesas))
    distritos_solo_ext = set(distritos_extranjeros) - set(distritos_mesas)
    distritos_solo_mesas = set(distritos_mesas) - set(distritos_extranjeros)

    print(f"   - Distritos en común: {len(distritos_comunes)}")
    print(f"   - Distritos solo en extranjeros: {len(distritos_solo_ext)}")
    print(f"   - Distritos solo en mesas: {len(distritos_solo_mesas)}")

    if distritos_solo_ext:
        print(f"   - Ejemplos distritos solo en extranjeros: {list(distritos_solo_ext)[:3]}")
    if distritos_solo_mesas:
        print(f"   - Ejemplos distritos solo en mesas: {list(distritos_solo_mesas)[:3]}")

if __name__ == "__main__":
    analizar_diferencias_union()
