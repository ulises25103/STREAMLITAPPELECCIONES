from __future__ import annotations
from pathlib import Path
import sys
import streamlit as st

project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.funciones_streamlit.funciones import (
    detectar_mesas_atipicas_por_partido,
    crear_dataframe,
)

from utils.constantes import BASE
# Cargar datos
df = crear_dataframe(BASE, ",", "DIPUTADOS PROVINCIALES", "SENADORES PROVINCIALES")
if df is None or df.empty:
    st.error("No se pudo cargar el dataset. Verificá la ruta/archivo en Streamlit Cloud.")
    st.stop()

st.title("Análisis de mesas por escuela")

# ----- FORM para inputs + botón APLICAR -----
with st.form("filtro_mesas"):
    partido = st.text_input("Partido a analizar", "FUERZA PATRIA")

    col1, col2 = st.columns(2)
    with col1:
        min_desvio = st.number_input("Desvío mínimo (≥)", value=-5.0, step=0.1)
    with col2:
        max_desvio = st.number_input("Desvío máximo (≤)", value=5.0, step=0.1)

    denominador = st.radio(
        "Denominador",
        ["Solo positivos", "Válidos (positivos + blancos)"],
        index=0,
        horizontal=True,
    )
    incluir_blancos = denominador == "Válidos (positivos + blancos)"

    # Botón que DISPARA el cálculo
    aplicar = st.form_submit_button("Aplicar")

# No hacer nada hasta que se apriete Aplicar
if not aplicar:
    st.info("Ajustá los parámetros y hacé clic en **Aplicar**.")

else:
    # Validación simple de rango
    if min_desvio > max_desvio:
        st.error("El desvío mínimo no puede ser mayor que el máximo.")
        st.stop()

    # ----- CÁLCULO (solo corre después de 'Aplicar') -----
    outliers = detectar_mesas_atipicas_por_partido(
        df,
        partido=partido,
        umbral_min=min_desvio,
        umbral_max=max_desvio,
        incluir_blancos_en_denominador=incluir_blancos,
    )

    # KPI con cantidad de mesas resultantes
    st.metric("Cantidad de mesas mostradas", len(outliers))

    st.subheader(f"Mesas con {min_desvio} ≤ desvío ≤ {max_desvio} pp en {partido}")

    try:
        st.dataframe(outliers, width="stretch")
    except TypeError:
        st.dataframe(outliers, use_container_width=True)

st.markdown(
    """
### 📊 Cómo se calcula el desvío de una mesa

1. **Porcentaje en la mesa (`pct_mesa`)**  
   Votos del partido en la mesa ÷ Total de votos válidos en la mesa × 100  

   *Ejemplo:* 20 votos del partido en una mesa con 100 válidos → **20 %**

---

2. **Porcentaje en la escuela (`pct_escuela`)**  
   Votos del partido en todas las mesas de la escuela ÷ Total de votos válidos en la escuela × 100  

   *Ejemplo:* 200 votos del partido en toda la escuela con 800 válidos → **25 %**

---

3. **Desvío en puntos porcentuales (`desvio_pp`)**  
   Porcentaje en la mesa − Porcentaje en la escuela  

   *Ejemplo:* 20 % (mesa) − 25 % (escuela) = **−5 pp**  
   ⇒ el partido rinde peor en esa mesa que en el promedio de su escuela.
"""
)
