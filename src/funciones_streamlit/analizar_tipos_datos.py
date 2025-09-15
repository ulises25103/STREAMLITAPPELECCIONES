import pandas as pd
import os
import re


def analizar_tipos_datos():
    """Analiza los diferentes tipos de valores en cada columna del CSV"""

    ruta_csv = os.path.join("utils", "data", "base_mesas_electores.csv")

    print("🔍 Analizando tipos de datos en el CSV...")
    df = pd.read_csv(ruta_csv)

    print(f"📊 Total de filas: {len(df):,}")
    print(f"📋 Columnas: {list(df.columns)}")
    print()

    # Análisis de cod_circ
    print("🏛️ ANÁLISIS DE COD_CIRC:")
    cod_circ_str = df["cod_circ"].astype(str)

    # Longitudes de códigos
    longitudes = cod_circ_str.str.len().value_counts().sort_index()
    print("📏 Longitudes de códigos de circuito:")
    for longitud, count in longitudes.items():
        print(f"  {longitud} dígitos: {count:,} registros")

    # Patrones de formato
    print("\n🎭 Patrones de formato:")
    patrones = {
        "Con ceros iniciales": cod_circ_str.str.startswith("0").sum(),
        "Solo números": cod_circ_str.str.match(r"^\d+$").sum(),
        "Con letras": cod_circ_str.str.match(r".*[a-zA-Z].*").sum(),
        "Con espacios": cod_circ_str.str.contains(" ").sum(),
    }

    for patron, count in patrones.items():
        print(f"  {patron}: {count:,}")

    # Ejemplos de cada tipo
    print("\n📝 Ejemplos de códigos de circuito:")
    print(
        "  Códigos con 2 dígitos:",
        cod_circ_str[cod_circ_str.str.len() == 2].unique()[:5],
    )
    print(
        "  Códigos con 5 dígitos:",
        cod_circ_str[cod_circ_str.str.len() == 5].unique()[:5],
    )
    print(
        "  Códigos que empiezan con 0:",
        cod_circ_str[cod_circ_str.str.startswith("0")].unique()[:5],
    )

    # Análisis de distrito
    print("\n🏢 ANÁLISIS DE DISTRITO:")
    distrito_str = df["distrito"].astype(str)

    valores_distrito = distrito_str.unique()
    print(f"📊 Valores únicos de distrito: {len(valores_distrito)}")
    print("📝 Ejemplos:", sorted(valores_distrito)[:10])

    # Ver si hay .0
    with_decimals = distrito_str.str.contains("\.0$").sum()
    print(f"  Con decimales (.0): {with_decimals:,}")
    print(f"  Sin decimales: {len(valores_distrito) - with_decimals:,}")

    # Análisis de nro_mesa
    print("\n🗳️ ANÁLISIS DE NRO_MESA:")
    nro_mesa_str = df["nro_mesa"].astype(str)

    valores_mesa = nro_mesa_str.unique()
    print(f"📊 Valores únicos de nro_mesa: {len(valores_mesa)}")

    with_decimals_mesa = nro_mesa_str.str.contains("\.0$").sum()
    print(f"  Con decimales (.0): {with_decimals_mesa:,}")
    print(f"  Sin decimales: {len(valores_mesa) - with_decimals_mesa:,}")

    # Análisis de establecimiento
    print("\n🏫 ANÁLISIS DE ESTABLECIMIENTO:")
    estab_str = df["establecimiento"].astype(str)

    print(f"📊 Nombres únicos de establecimientos: {estab_str.nunique():,}")

    # Buscar caracteres especiales
    with_accents = estab_str.str.contains(r"[áéíóúÁÉÍÓÚñÑ]").sum()
    with_numbers = estab_str.str.contains(r"\d").sum()
    with_symbols = estab_str.str.contains(r"[^\w\s]").sum()

    print(f"  Con acentos: {with_accents:,}")
    print(f"  Con números: {with_numbers:,}")
    print(f"  Con símbolos especiales: {with_symbols:,}")

    # Análisis de tipo
    print("\n🏷️ ANÁLISIS DE TIPO:")
    tipos_unicos = df["tipo"].unique()
    print(f"📊 Tipos únicos: {tipos_unicos}")
    print("📈 Distribución:")
    for tipo in tipos_unicos:
        count = (df["tipo"] == tipo).sum()
        print(f"  {tipo}: {count:,} registros")

    # Análisis de cantidad_electores
    print("\n👥 ANÁLISIS DE CANTIDAD_ELECTORES:")
    electores = df["cantidad_electores"]

    print(f"📊 Estadísticas:")
    print(f"  Mínimo: {electores.min():,}")
    print(f"  Máximo: {electores.max():,}")
    print(f"  Promedio: {electores.mean():,.1f}")
    print(f"  Mediana: {electores.median():,.0f}")
    print(f"  Total: {electores.sum():,}")

    # Verificar si hay valores nulos
    print("\n🚨 VERIFICACIÓN DE VALORES NULOS:")
    nulos = df.isnull().sum()
    for col, count in nulos.items():
        if count > 0:
            print(f"  {col}: {count:,} valores nulos")

    if nulos.sum() == 0:
        print("  ✅ No hay valores nulos en el dataset")

    print("\n" + "=" * 60)
    print("💡 RECOMENDACIONES PARA NORMALIZACIÓN:")
    print("=" * 60)

    print("1. COD_CIRC:")
    print("   - Convertir a string y quitar ceros iniciales")
    print("   - Mantener formato consistente (sin ceros a la izquierda)")

    print("\n2. DISTRITO:")
    print("   - Convertir a string y quitar '.0'")
    print("   - Mantener como string para evitar pérdida de precisión")

    print("\n3. NRO_MESA:")
    print("   - Convertir a string y quitar '.0'")
    print("   - Mantener como string")

    print("\n4. ESTABLECIMIENTO:")
    print("   - Normalizar mayúsculas/minúsculas")
    print("   - Quitar espacios extra al inicio/fin")
    print("   - Considerar normalizar acentos si es necesario")

    print("\n5. TIPO:")
    print("   - Ya parece consistente (NATIVA/EXTRANJERA)")


def crear_clave_normalizada():
    """Crea una clave única con normalización de datos"""

    ruta_csv = os.path.join("utils", "data", "base_mesas_electores.csv")

    df = pd.read_csv(ruta_csv)

    # Normalizar cada columna
    df_normalizado = df.copy()

    # Normalizar cod_circ: quitar ceros iniciales
    df_normalizado["cod_circ_norm"] = df["cod_circ"].astype(str).str.lstrip("0")

    # Normalizar distrito: quitar .0
    df_normalizado["distrito_norm"] = df["distrito"].astype(str).str.replace(".0", "")

    # Normalizar nro_mesa: quitar .0
    df_normalizado["nro_mesa_norm"] = df["nro_mesa"].astype(str).str.replace(".0", "")

    # Normalizar establecimiento: quitar espacios extra y estandarizar mayúsculas
    df_normalizado["establecimiento_norm"] = (
        df["establecimiento"].astype(str).str.strip().str.upper()
    )

    # Crear clave normalizada
    df_normalizado["clave_normalizada"] = (
        df_normalizado["cod_circ_norm"]
        + "|"
        + df_normalizado["distrito_norm"]
        + "|"
        + df_normalizado["establecimiento_norm"]
        + "|"
        + df_normalizado["nro_mesa_norm"]
        + "|"
        + df_normalizado["tipo"].astype(str)
    )

    print("🔑 CLAVE NORMALIZADA:")
    print(
        "📊 Claves únicas normalizadas:", df_normalizado["clave_normalizada"].nunique()
    )

    # Comparar con clave original
    df_original = df.copy()
    df_original["clave_original"] = (
        df["cod_circ"].astype(str)
        + "|"
        + df["distrito"].astype(str)
        + "|"
        + df["establecimiento"].astype(str)
        + "|"
        + df["nro_mesa"].astype(str)
        + "|"
        + df["tipo"].astype(str)
    )

    print("📊 Claves únicas originales:", df_original["clave_original"].nunique())

    diferencia = (
        df_normalizado["clave_normalizada"].nunique()
        - df_original["clave_original"].nunique()
    )
    print(f"📈 Diferencia: {diferencia:,} claves adicionales detectadas")

    return df_normalizado


if __name__ == "__main__":
    analizar_tipos_datos()
    print("\n" + "=" * 60)
    crear_clave_normalizada()
