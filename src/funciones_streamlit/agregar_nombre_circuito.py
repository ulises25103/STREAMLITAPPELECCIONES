import pandas as pd
import os
import sys

# Agregar la ruta del proyecto para poder importar constantes
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from utils.constantes import DISTRITOS


def agregar_nombre_circuito():
    """Agrega columna nombre_circuito al archivo base_mesas_electores_normalizado.csv usando el mapeo DISTRITOS"""

    ruta_csv = os.path.join("utils", "data", "base_mesas_electores_normalizado.csv")

    print("🔍 Leyendo archivo CSV normalizado...")
    df = pd.read_csv(ruta_csv)

    print(f"📊 Archivo actual: {len(df):,} filas")
    print(f"📋 Columnas actuales: {list(df.columns)}")
    print()

    # Convertir distrito a int para el mapeo (ya está normalizado sin .0)
    df["distrito_int"] = df["distrito"].astype(int)

    print("🏛️ Agregando columna nombre_circuito...")

    # Usar map para asignar los nombres de circuito
    df["nombre_circuito"] = df["distrito_int"].map(DISTRITOS)

    # Verificar si hay distritos sin mapeo
    distritos_sin_mapeo = df[df["nombre_circuito"].isnull()]["distrito_int"].unique()

    if len(distritos_sin_mapeo) > 0:
        print(f"⚠️ Distritos sin mapeo encontrado: {distritos_sin_mapeo}")
        print("Esto puede indicar que falta algún distrito en la constante DISTRITOS")
    else:
        print("✅ Todos los distritos tienen mapeo correcto")

    print(f"\n📊 Estadísticas:")
    print(f"  Distritos únicos: {df['distrito_int'].nunique():,}")
    print(f"  Nombres de circuito únicos: {df['nombre_circuito'].nunique():,}")

    # Limpiar columna temporal antes de reorganizar
    df = df.drop("distrito_int", axis=1)

    # Mostrar algunos ejemplos
    print("\n📝 Ejemplos de mapeo:")
    ejemplos = df[["distrito", "nombre_circuito"]].drop_duplicates().head(10)
    for _, row in ejemplos.iterrows():
        print(f"  Distrito {int(row['distrito']):3d} -> {row['nombre_circuito']}")

    # Reorganizar columnas: poner nombre_circuito después de distrito
    columnas_ordenadas = [
        "cod_circ",
        "distrito",
        "nombre_circuito",
        "establecimiento",
        "nro_mesa",
        "cantidad_electores",
        "tipo",
    ]

    df_final = df[columnas_ordenadas]

    print("\n📋 Columnas finales:")
    print(f"  {list(df_final.columns)}")

    # Sobrescribir el archivo normalizado con la nueva columna
    ruta_normalizado = os.path.join(
        "utils", "data", "base_mesas_electores_normalizado.csv"
    )
    print(
        f"\n💾 Actualizando archivo normalizado con nombres de circuito: {ruta_normalizado}"
    )

    df_final.to_csv(ruta_normalizado, index=False)
    print("✅ Archivo normalizado actualizado exitosamente")

    # Estadísticas finales
    print(f"\n📊 Resumen final:")
    print(f"  Total de mesas: {len(df_final):,}")
    print(f"  Circuitos únicos: {df_final['cod_circ'].nunique():,}")
    print(f"  Distritos únicos: {df_final['distrito'].nunique():,}")
    print(f"  Nombres de circuito únicos: {df_final['nombre_circuito'].nunique():,}")
    print(f"  Establecimientos únicos: {df_final['establecimiento'].nunique():,}")
    print(f"  Total electores: {df_final['cantidad_electores'].sum():,}")

    return df_final


def verificar_mapeo_completo():
    """Verifica que todos los distritos del CSV estén en la constante DISTRITOS"""

    ruta_csv = os.path.join("utils", "data", "base_mesas_electores_normalizado.csv")
    df = pd.read_csv(ruta_csv)

    distritos_csv = set(df["distrito"].astype(int).unique())
    distritos_constante = set(DISTRITOS.keys())

    print("🔍 Verificación de mapeo completo:")
    print(f"  Distritos en CSV: {len(distritos_csv)}")
    print(f"  Distritos en constante: {len(distritos_constante)}")

    # Distritos que están en CSV pero no en constante
    faltantes_en_constante = distritos_csv - distritos_constante
    if faltantes_en_constante:
        print(
            f"  ❌ Distritos en CSV pero no en constante: {sorted(faltantes_en_constante)}"
        )

    # Distritos que están en constante pero no en CSV
    faltantes_en_csv = distritos_constante - distritos_csv
    if faltantes_en_csv:
        print(
            f"  ℹ️ Distritos en constante pero no en CSV: {len(faltantes_en_csv)} distritos"
        )

    if not faltantes_en_constante:
        print("  ✅ Mapeo completo: Todos los distritos del CSV están en la constante")

    return len(faltantes_en_constante) == 0


if __name__ == "__main__":
    print("🏛️ AGREGANDO NOMBRES DE CIRCUITO AL ARCHIVO NORMALIZADO")
    print("=" * 60)

    # Verificar mapeo primero
    mapeo_completo = verificar_mapeo_completo()
    print()

    if mapeo_completo:
        # Proceder con la agregación
        df_resultado = agregar_nombre_circuito()
    else:
        print("❌ Error: Hay distritos sin mapeo. Revisa la constante DISTRITOS.")
        df_resultado = None

    print("\n" + "=" * 60)
    print("✅ Proceso completado")
