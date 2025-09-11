import pandas as pd
import os
from pathlib import Path


def unir_extranjeros_con_mesas():
    """
    Une los datos de extranjeros con las mesas electorales,
    sumando los electores extranjeros a las mesas existentes.
    """

    # Cambiar al directorio del proyecto
    os.chdir(Path(__file__).parent)

    print("🚀 Iniciando proceso de unión de datos...")

    # Rutas de archivos
    ruta_extranjeros = "utils/data/padron_extranjeros_2025.csv"
    ruta_mesas = "utils/data/mesas_electores_reducido.csv"
    ruta_salida = "utils/data/mesas_con_extranjeros.csv"

    # 1. Cargar datos de extranjeros
    print("📖 Cargando datos de extranjeros...")
    try:
        df_extranjeros = pd.read_csv(ruta_extranjeros, encoding="utf-8")
        print(f"✅ Extranjeros cargados: {len(df_extranjeros):,} filas")
        print(f"📊 Columnas: {list(df_extranjeros.columns)}")
    except Exception as e:
        print(f"❌ Error al cargar extranjeros: {e}")
        return None

    # 2. Cargar datos de mesas
    print("\n📖 Cargando datos de mesas...")
    try:
        df_mesas = pd.read_csv(ruta_mesas, encoding="utf-8")
        print(f"✅ Mesas cargadas: {len(df_mesas):,} filas")
        print(f"📊 Columnas: {list(df_mesas.columns)}")
    except Exception as e:
        print(f"❌ Error al cargar mesas: {e}")
        return None

    # 3. Preparar dataframes para la combinación
    print("\n🔢 Preparando dataframes...")

    # Agregar columnas faltantes a df_mesas
    if "extranjeros" not in df_mesas.columns:
        df_mesas["extranjeros"] = 0
    if "electores_total" not in df_mesas.columns:
        df_mesas["electores_total"] = df_mesas["electores"]

    # Agrupar extranjeros por mesa
    print("\n🔢 Agrupando extranjeros por mesa...")
    columnas_agrupacion = ["nombre_distrito", "cod_circ", "nro_mesa", "establecimiento"]

    # Verificar que las columnas existan en ambos dataframes
    for col in columnas_agrupacion:
        if col not in df_extranjeros.columns:
            print(f"⚠️  Columna '{col}' no encontrada en extranjeros")
        if col not in df_mesas.columns:
            print(f"⚠️  Columna '{col}' no encontrada en mesas")

    # Contar extranjeros por mesa
    extranjeros_por_mesa = (
        df_extranjeros.groupby(columnas_agrupacion)
        .size()
        .reset_index(name="extranjeros")
    )
    print(
        f"✅ Agrupación completada: {len(extranjeros_por_mesa):,} mesas con extranjeros"
    )

    # Mostrar estadísticas
    print("\n📈 Estadísticas de extranjeros por mesa:")
    print(f"   - Total de mesas con extranjeros: {len(extranjeros_por_mesa):,}")
    print(f"   - Total de extranjeros: {extranjeros_por_mesa['extranjeros'].sum():,}")
    print(f"   - Promedio por mesa: {extranjeros_por_mesa['extranjeros'].mean():.1f}")
    print(f"   - Máximo por mesa: {extranjeros_por_mesa['extranjeros'].max()}")

    # 4. Preparar mesas de extranjeros para agregar
    print("\n🔗 Preparando mesas de extranjeros para agregar...")

    # Crear dataframe con las mesas de extranjeros
    # Necesitamos agregar la columna 'seccion_electoral' que falta en extranjeros
    extranjeros_por_mesa["seccion_electoral"] = "EXTRANJEROS"  # Valor por defecto
    extranjeros_por_mesa["electores"] = (
        0  # Las mesas de extranjeros no tienen electores locales
    )
    extranjeros_por_mesa["electores_total"] = extranjeros_por_mesa["extranjeros"]

    # Reordenar columnas para que coincidan con df_mesas
    columnas_ordenadas = [
        "nombre_distrito",
        "seccion_electoral",
        "cod_circ",
        "establecimiento",
        "nro_mesa",
        "electores",
        "extranjeros",
        "electores_total",
    ]
    extranjeros_por_mesa = extranjeros_por_mesa[columnas_ordenadas]

    # 5. Combinar dataframes (agregar mesas de extranjeros al final)
    print("\n➕ Agregando mesas de extranjeros...")
    df_unido = pd.concat([df_mesas, extranjeros_por_mesa], ignore_index=True)

    # Agregar columna de extranjeros = 0 para las mesas originales
    if "extranjeros" not in df_mesas.columns:
        df_unido["extranjeros"] = df_unido["extranjeros"].fillna(0).astype(int)
        df_unido["electores_total"] = (
            df_unido["electores_total"].fillna(df_unido["electores"]).astype(int)
        )

    # Mostrar resumen final
    print("\n📊 Resumen final:")
    print(f"   - Mesas originales: {len(df_mesas):,}")
    print(f"   - Mesas de extranjeros agregadas: {len(extranjeros_por_mesa):,}")
    print(f"   - Mesas totales: {len(df_unido):,}")
    print(
        f"   - Electores originales: {df_unido[df_unido['seccion_electoral'] != 'EXTRANJEROS']['electores'].sum():,}"
    )
    print(f"   - Extranjeros agregados: {extranjeros_por_mesa['extranjeros'].sum():,}")
    print(f"   - Electores totales: {df_unido['electores_total'].sum():,}")

    # 6. Guardar resultado
    print(f"\n💾 Guardando resultado en: {ruta_salida}")
    try:
        df_unido.to_csv(ruta_salida, index=False, encoding="utf-8")
        print("✅ Archivo guardado exitosamente!")

        # Mostrar primeras filas del resultado
        print("\n📋 Primeras 5 filas del resultado:")
        print(df_unido.head().to_string(index=False))

    except Exception as e:
        print(f"❌ Error al guardar archivo: {e}")
        return None

    return df_unido


if __name__ == "__main__":
    resultado = unir_extranjeros_con_mesas()
    if resultado is not None:
        print("\n🎉 Proceso completado exitosamente!")
    else:
        print("\n❌ El proceso falló.")
