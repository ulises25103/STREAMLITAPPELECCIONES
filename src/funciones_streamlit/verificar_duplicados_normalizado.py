import pandas as pd
import os


def normalizar_valores(df):
    """Normaliza los valores para crear claves consistentes"""

    df_norm = df.copy()

    # Normalizar cod_circ: quitar ceros iniciales
    df_norm["cod_circ_norm"] = df["cod_circ"].astype(str).str.lstrip("0")

    # Normalizar distrito: quitar .0
    df_norm["distrito_norm"] = df["distrito"].astype(str).str.replace(".0", "")

    # Normalizar nro_mesa: quitar .0
    df_norm["nro_mesa_norm"] = df["nro_mesa"].astype(str).str.replace(".0", "")

    # Normalizar establecimiento: quitar espacios extra y estandarizar mayúsculas
    df_norm["establecimiento_norm"] = (
        df["establecimiento"].astype(str).str.strip().str.upper()
    )

    return df_norm


def verificar_duplicados_normalizado():
    """Verifica duplicados usando normalización de datos"""

    ruta_original = os.path.join("utils", "data", "base_mesas_electores.csv")

    print("🔍 Leyendo archivo CSV...")
    df = pd.read_csv(ruta_original)

    print(f"📊 Archivo original: {len(df):,} filas")
    print()

    # Normalizar datos
    print("🔄 Normalizando datos...")
    df_norm = normalizar_valores(df)

    # Crear clave normalizada
    print("🔑 Creando clave normalizada...")
    df_norm["clave_normalizada"] = (
        df_norm["cod_circ_norm"]
        + "|"
        + df_norm["distrito_norm"]
        + "|"
        + df_norm["establecimiento_norm"]
        + "|"
        + df_norm["nro_mesa_norm"]
        + "|"
        + df_norm["tipo"].astype(str)
    )

    print(f"🎯 Total de claves normalizadas creadas: {len(df_norm):,}")
    print(f"🔢 Claves únicas normalizadas: {df_norm['clave_normalizada'].nunique():,}")
    print()

    # Comparar con clave original
    df["clave_original"] = (
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

    print(f"📊 Claves únicas originales: {df['clave_original'].nunique():,}")
    diferencia = df_norm["clave_normalizada"].nunique() - df["clave_original"].nunique()
    print(
        f"📈 Diferencia por normalización: {diferencia:,} mesas adicionales detectadas"
    )
    print()

    # Verificar duplicados con clave normalizada
    duplicados_norm = df_norm[
        df_norm.duplicated(subset=["clave_normalizada"], keep=False)
    ]
    duplicados_count_norm = len(duplicados_norm)

    print(f"🚨 Filas con claves duplicadas (normalizadas): {duplicados_count_norm:,}")

    if duplicados_count_norm > 0:
        print("\n📋 Estadísticas de duplicados normalizados:")
        stats_duplicados_norm = (
            duplicados_norm.groupby("clave_normalizada")
            .agg({"cantidad_electores": ["count", "sum", "min", "max"]})
            .reset_index()
        )

        print(
            f"🔍 Total de mesas duplicadas (normalizadas): {len(stats_duplicados_norm):,}"
        )
        print(
            f"💰 Suma total de electores en duplicados: {stats_duplicados_norm[('cantidad_electores', 'sum')].sum():,}"
        )
        print()

        # Mostrar algunos ejemplos
        print("📝 Ejemplos de duplicados encontrados:")
        ejemplos = duplicados_norm.groupby("clave_normalizada").head(2)
        for _, row in ejemplos.head(8).iterrows():
            print(f"  Mesa: {row['clave_normalizada']}")
            print(f"  Electores: {row['cantidad_electores']}")
            print(
                f"  Original cod_circ: {row['cod_circ']} -> Normalizado: {row['cod_circ_norm']}"
            )
            print()

    # Procesar duplicados sumando electores
    if duplicados_count_norm > 0:
        print("\n🔄 Procesando duplicados normalizados - sumando electores...")
        # Separar mesas únicas y duplicadas
        df_unicos_norm = df_norm[
            ~df_norm.duplicated(subset=["clave_normalizada"], keep=False)
        ].copy()
        df_duplicados_norm = df_norm[
            df_norm.duplicated(subset=["clave_normalizada"], keep=False)
        ].copy()

        print(f"📊 Mesas sin duplicados: {len(df_unicos_norm):,}")
        print(
            f"📊 Mesas con duplicados: {len(df_duplicados_norm.groupby('clave_normalizada')):,}"
        )

        # Agrupar duplicados y sumar electores
        df_duplicados_agrupados_norm = (
            df_duplicados_norm.groupby("clave_normalizada")
            .agg(
                {
                    "cod_circ_norm": "first",
                    "distrito_norm": "first",
                    "establecimiento_norm": "first",
                    "nro_mesa_norm": "first",
                    "tipo": "first",
                    "cantidad_electores": "sum",  # Sumar los electores
                }
            )
            .reset_index()
        )

        print(
            f"💰 Electores totales en mesas únicas: {df_unicos_norm['cantidad_electores'].sum():,}"
        )
        print(
            f"💰 Electores totales en mesas duplicadas (sumados): {df_duplicados_agrupados_norm['cantidad_electores'].sum():,}"
        )

        # Combinar mesas únicas con duplicadas agrupadas
        df_final_norm = pd.concat(
            [df_unicos_norm, df_duplicados_agrupados_norm], ignore_index=True
        )

        # Crear DataFrame final con columnas originales normalizadas
        df_final_norm["cod_circ"] = df_final_norm["cod_circ_norm"]
        df_final_norm["distrito"] = df_final_norm["distrito_norm"]
        df_final_norm["nro_mesa"] = df_final_norm["nro_mesa_norm"]
        df_final_norm["establecimiento"] = df_final_norm["establecimiento_norm"]

        # Mantener solo las columnas originales
        columnas_finales = [
            "cod_circ",
            "distrito",
            "establecimiento",
            "nro_mesa",
            "cantidad_electores",
            "tipo",
        ]
        df_final_norm = df_final_norm[columnas_finales]

        print(
            f"\n✅ DataFrame final normalizado creado con {len(df_final_norm):,} filas"
        )
        print(f"📊 Verificación: claves únicas finales: {len(df_final_norm):,}")

    else:
        df_final_norm = df.copy()

    mesas_finales_norm = len(df_final_norm)

    print(f"\n✅ Mesas finales después del proceso normalizado: {mesas_finales_norm:,}")
    print(f"📉 Mesas consolidadas: {len(df) - mesas_finales_norm:,}")
    print(f"💰 Total electores finales: {df_final_norm['cantidad_electores'].sum():,}")
    print()

    # Crear nuevo archivo normalizado
    ruta_normalizado = os.path.join(
        "utils", "data", "base_mesas_electores_normalizado.csv"
    )
    print(f"💾 Creando archivo normalizado: {ruta_normalizado}")

    df_final_norm.to_csv(ruta_normalizado, index=False)
    print("✅ Archivo normalizado creado exitosamente")
    print(f"📊 Mesas en archivo normalizado: {mesas_finales_norm:,}")

    return mesas_finales_norm, duplicados_count_norm


if __name__ == "__main__":
    verificar_duplicados_normalizado()
