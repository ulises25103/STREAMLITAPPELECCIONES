from pathlib import Path

PROJECT_PATH = Path(__file__).parents[1].resolve()  # Raiz del proyecto
UTILS_PATH = PROJECT_PATH / "utils"
DATA_PATH = UTILS_PATH / "data"  # Ruta donde se almacena los datos
SRC_PATH = PROJECT_PATH / "src"  # Ruta de funciones
STREAMLIT_PATH = PROJECT_PATH / "streamlit"  # App Streamlit

# BASES
BASE =  DATA_PATH / 'Base_Elecciones.zip'
ELECTORES_PATH = DATA_PATH / "ELECTORES.csv"

# Lista de municipios del AMBA (Provincia de Buenos Aires)
MUNICIPIOS_AMBA = [
    # Conurbano Bonaerense y zona metropolitana (sin incluir CABA)
    "ALMIRANTE BROWN",
    "AVELLANEDA",
    "BERAZATEGUI",
    "BERISSO",
    "BRANDSEN",
    "CAMPANA",
    "CAÑUELAS",
    "ENSENADA",
    "ESCOBAR",
    "ESTEBAN ECHEVERRIA",
    "EXALTACION DE LA CRUZ",
    "EZEIZA",
    "FLORENCIO VARELA",
    "GENERAL LAS HERAS",
    "GENERAL RODRIGUEZ",
    "GENERAL SAN MARTIN",
    "HURLINGHAM",
    "ITUZAINGO",
    "JOSE C. PAZ",
    "LA MATANZA",
    "LANUS",
    "LA PLATA",
    "LOMAS DE ZAMORA",
    "LUJAN",
    "MARCOS PAZ",
    "MALVINAS ARGENTINAS",
    "MERLO",
    "MORENO",
    "MORON",
    "PILAR",
    "PRESIDENTE PERON",
    "QUILMES",
    "SAN FERNANDO",
    "SAN ISIDRO",
    "SAN MIGUEL",
    "SAN VICENTE",
    "TIGRE",
    "TRES DE FEBRERO",
    "VICENTE LOPEZ",
    "ZARATE",
]
