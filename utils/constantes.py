from pathlib import Path

PROJECT_PATH = Path(__file__).parents[1].resolve()  # Raiz del proyecto
UTILS_PATH = PROJECT_PATH / "utils"
DATA_PATH = UTILS_PATH / "data"  # Ruta donde se almacena los datos
SRC_PATH = PROJECT_PATH / "src"  # Ruta de funciones
STREAMLIT_PATH = PROJECT_PATH / "streamlit"  # App Streamlit

# BASES
BASE =  DATA_PATH / 'Base_Elecciones.csv'
ELECTORES_PATH = DATA_PATH / "ELECTORES.csv"
