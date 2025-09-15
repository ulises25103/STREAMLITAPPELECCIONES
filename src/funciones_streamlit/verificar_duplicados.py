import pandas as pd
import os


def verificar_duplicados():
    """Verifica duplicados en el archivo base_mesas_electores.csv y crea un archivo limpio"""

    # Ruta del archivo original
    ruta_original = os.path.join("utils", "data", "base_mesas_electores.csv")

    print("🔍 Leyendo archivo CSV...")
    df = pd.read_csv(ruta_original)

    print(f"📊 Archivo original: {len(df):,} filas")
    print(f"📋 Columnas: {list(df.columns)}")
    print()

    # Crear clave única convirtiendo todo a string
    print("🔑 Creando clave única...")
    df["clave_unica"] = (
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

    print(f"🎯 Total de claves únicas creadas: {len(df):,}")
    print(f"🔢 Claves únicas distintas: {df['clave_unica'].nunique():,}")
    print()

    # Verificar duplicados
    duplicados = df[df.duplicated(subset=["clave_unica"], keep=False)]
    duplicados_count = len(duplicados)

    print(f"🚨 Filas con claves duplicadas: {duplicados_count:,}")

    if duplicados_count > 0:
        print("\n📋 Ejemplos de duplicados encontrados:")
        # Mostrar algunos ejemplos
        ejemplos_duplicados = duplicados.groupby("clave_unica").head(2)
        for _, row in ejemplos_duplicados.head(6).iterrows():
            print(f"  Clave: {row['clave_unica']}")
            print(f"  Electores: {row['cantidad_electores']}")
            print()

        # Estadísticas por tipo de duplicado
        print("📊 Estadísticas de duplicados:")
        stats_duplicados = (
            duplicados.groupby("clave_unica")
            .agg({"cantidad_electores": ["count", "sum", "min", "max", list]})
            .reset_index()
        )

        print(f"🔍 Total de mesas duplicadas: {len(stats_duplicados):,}")
        print(
            f"💰 Suma total de electores en duplicados: {stats_duplicados[('cantidad_electores', 'sum')].sum():,}"
        )
        print()

    # Procesar duplicados sumando electores
    if duplicados_count > 0:
        print("\n🔄 Procesando duplicados - sumando electores...")

        # Separar mesas únicas y duplicadas
        df_unicos = df[~df.duplicated(subset=["clave_unica"], keep=False)].copy()
        df_duplicados = df[df.duplicated(subset=["clave_unica"], keep=False)].copy()

        print(f"📊 Mesas sin duplicados: {len(df_unicos):,}")
        print(f"📊 Mesas con duplicados: {len(df_duplicados.groupby('clave_unica')):,}")

        # Agrupar duplicados y sumar electores
        df_duplicados_agrupados = (
            df_duplicados.groupby("clave_unica")
            .agg(
                {
                    "cod_circ": "first",
                    "distrito": "first",
                    "establecimiento": "first",
                    "nro_mesa": "first",
                    "tipo": "first",
                    "cantidad_electores": "sum",  # Sumar los electores
                }
            )
            .reset_index()
        )

        print(
            f"💰 Electores totales en mesas únicas: {df_unicos['cantidad_electores'].sum():,}"
        )
        print(
            f"💰 Electores totales en mesas duplicadas (sumados): {df_duplicados_agrupados['cantidad_electores'].sum():,}"
        )
        print(
            f"💰 Electores totales en mesas duplicadas (original): {df_duplicados['cantidad_electores'].sum():,}"
        )

        # Combinar mesas únicas con duplicadas agrupadas
        df_final = pd.concat([df_unicos, df_duplicados_agrupados], ignore_index=True)

        print(f"\n✅ DataFrame final creado con {len(df_final):,} filas")
        print(
            f"📊 Verificación: claves únicas en final: {df_final['clave_unica'].nunique():,}"
        )

    else:
        df_final = df.copy()

    mesas_finales = len(df_final)

    print(f"\n✅ Mesas finales después del proceso: {mesas_finales:,}")
    print(f"📉 Mesas consolidadas: {len(df) - mesas_finales:,}")
    print(f"💰 Total electores finales: {df_final['cantidad_electores'].sum():,}")
    print()

    # Crear nuevo archivo
    ruta_limpio = os.path.join("utils", "data", "base_mesas_electores_consolidado.csv")
    print(f"💾 Creando archivo consolidado: {ruta_limpio}")

    df_final.to_csv(ruta_limpio, index=False)
    print("✅ Archivo consolidado creado exitosamente")
    print(f"📊 Mesas en archivo consolidado: {mesas_finales:,}")

    return mesas_finales, duplicados_count


if __name__ == "__main__":
    verificar_duplicados()
