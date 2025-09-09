import pandas as pd
import numpy as np
from pathlib import Path


def abrir_archivo_elecciones():
    """
    Abre el archivo Excel de elecciones
    """
    try:
        # Ruta del archivo
        archivo_path = "Base_Elecciones_DiputadosySenadores.xlsx"

        # Verificar que el archivo existe
        if not Path(archivo_path).exists():
            print(f"Error: No se encontró el archivo {archivo_path}")
            return None

        df = pd.read_excel(archivo_path)
        return df

    except Exception as e:
        print(f"Error al abrir el archivo: {e}")
        return None


def contar_votos_por_tipo_eleccion(df: pd.DataFrame, output_file: str):
    """
    Cuenta los votos por tipo de elección, separando votos válidos (Positivo + En Blanco)
    de votos Nulo, según la columna 'Tipo_Voto'.
    """
    try:
        # Asegurar tipo numérico en votos
        df["votos"] = pd.to_numeric(df["votos"], errors="coerce").fillna(0).astype(int)

        # Filtrar por tipo de voto
        df_validos = df[df["Tipo_Voto"].isin(["Positivo", "En Blanco"])].copy()
        df_nulos = df[df["Tipo_Voto"] == "Nulo"].copy()

        # Agrupar y sumar votos por tipo de elección
        votos_validos = df_validos.groupby("Tipo_elección")["votos"].sum().reset_index()
        votos_validos.rename(columns={"votos": "votos_validos"}, inplace=True)

        votos_nulos = df_nulos.groupby("Tipo_elección")["votos"].sum().reset_index()
        votos_nulos.rename(columns={"votos": "votos_nulos"}, inplace=True)

        # Unir ambos resultados (outer join para no perder elecciones sin nulos o sin válidos)
        resumen = pd.merge(
            votos_validos, votos_nulos, on="Tipo_elección", how="outer"
        ).fillna(0)
        resumen[["votos_validos", "votos_nulos"]] = resumen[
            ["votos_validos", "votos_nulos"]
        ].astype(int)

        # Guardar CSV si no existe
        if not Path(output_file).exists():
            resumen.to_csv(output_file, index=False)
            print(f"El archivo CSV se ha guardado en: {output_file}")
        else:
            print(f"El archivo CSV ya existe: {output_file}")

    except KeyError:
        print(
            "Error: Faltan columnas necesarias en el DataFrame ('votos', 'Tipo_Voto', 'Tipo_elección')."
        )
    except Exception as e:
        print(f"Error al contar los votos por tipo de elección: {e}")


def contar_total_electores(csv_path: str) -> int:
    """
    Cuenta la cantidad total de electores a partir de un CSV con separador ';'.
    Asume que 'Electores' usa punto como separador de miles.
    """
    try:
        # Leer CSV con separador punto y coma
        df = pd.read_csv(csv_path, sep=";")

        # Limpiar columna 'Electores': eliminar puntos, convertir a int
        df["Electores"] = (
            df["Electores"]
            .astype(str)
            .str.replace(".", "", regex=False)  # quita puntos separadores de miles
            .str.replace(",", "", regex=False)  # por si hay comas también
        )
        df["Electores"] = (
            pd.to_numeric(df["Electores"], errors="coerce").fillna(0).astype(int)
        )

        # Sumar total
        total_electores = df["Electores"].sum()

        return total_electores

    except Exception as e:
        print(f"Error al procesar el archivo de electores: {e}")
        return None


def sumar_votos_legisladores(csv_path: str) -> int:
    """
    Lee el CSV con los votos por tipo de elección y suma los votos válidos + nulos
    de Diputados y Senadores Provinciales.
    """
    try:
        # Cargar el CSV
        legisladores = pd.read_csv(csv_path)

        # Asegurar que las columnas sean numéricas
        legisladores["votos_validos"] = pd.to_numeric(
            legisladores["votos_validos"], errors="coerce"
        ).fillna(0)
        # Sumar total
        total = int(
            legisladores["votos_validos"].sum()
        )

        return total

    except Exception as e:
        print(f"Error al sumar votos de legisladores: {e}")
        return None


df = abrir_archivo_elecciones()
if df is not None:
    output_file_votos_por_cargo = "votos_por_tipo_2025.csv"  # Nombre del archivo CSV de salida
    contar_votos_por_tipo_eleccion(df, output_file_votos_por_cargo)
    ruta_archivo = "ELECTORES.CSV"
    total_electores = contar_total_electores(ruta_archivo)
    print(total_electores)
    ruta_archivo2 = "votos_por_tipo_2025.csv"
    total_votos = sumar_votos_legisladores(ruta_archivo2)
    print(total_votos)
    participacion_legislativa = (total_votos / total_electores) * 100
    print(participacion_legislativa)
