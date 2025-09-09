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

df = crear_dataframe(BASE, ",", "DIPUTADOS PROVINCIALES", "SENADORES PROVINCIALES")
if df is None or df.empty:
    st.error(
        "No se pudo cargar el dataset. Verificá la ruta/archivo en Streamlit Cloud."
    )
    st.stop()

partido = st.text_input("Partido a analizar", "FUERZA PATRIA")

# Inputs de rango
min_desvio = st.number_input("Desvío mínimo (≥)", value=-5.0, step=0.1)
max_desvio = st.number_input("Desvío máximo (≤)", value=5.0, step=0.1)

denominador = st.radio(
    "Denominador",
    ["Solo positivos", "Válidos (positivos + blancos)"],
    index=0,
)
incluir_blancos = denominador == "Válidos (positivos + blancos)"

outliers = detectar_mesas_atipicas_por_partido(
    df,
    partido=partido,
    umbral_min=min_desvio,
    umbral_max=max_desvio,
    incluir_blancos_en_denominador=incluir_blancos,
)

# Filtrar por rango definido por el usuario
filtro = outliers[
    (outliers["desvio_pp"] >= min_desvio) & (outliers["desvio_pp"] <= max_desvio)
]
cantidad_mesas = len(filtro)

st.metric(label="Cantidad de mesas mostradas", value=cantidad_mesas)
st.subheader(f"Mesas con {min_desvio} ≤ desvío ≤ {max_desvio} pp en {partido}")
st.dataframe(filtro, width="stretch")

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
