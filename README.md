# Election Data Analysis System

A comprehensive Python-based system for processing and analyzing electoral data for the 2025 elections in Argentina. Built with Streamlit, this application provides tools for data validation, normalization, and visualization of electoral results.

## Features

### 🔍 Data Analysis

- **Circuit Code Analysis**: Validation and normalization of electoral circuit codes
- **District Analysis**: Processing of district-level electoral data
- **Polling Station Analysis**: Validation of polling station numbers and information
- **Institution Analysis**: Processing of educational institution data used as polling places
- **Voter Analysis**: Statistical analysis of voter registration data

### 📊 Electoral Categories

- **Diputados y Senadores** (Deputies and Senators)
- **Concejales Municipales** (Municipal Councilors)
- **Escuelas** (Schools/Polling Places)
- **Electores** (Voters)

### 🛠️ Data Processing

- CSV data validation and cleaning
- Duplicate detection and removal
- Data normalization for consistent formatting
- Statistical analysis and reporting

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd eleccion
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

1. Start the Streamlit application:

```bash
streamlit run streamlit/Inicio.py
```

2. Open your browser and navigate to the provided local URL

### Data Upload

The application accepts the following file formats:

- CSV files
- Excel files (.xlsx)
- ZIP archives containing data files

**Required Files:**

- `Base_Elecciones.csv` - Main electoral results database
- `ELECTORES.csv` - Voter registration data

⚠️ **Important**: Maintain exact file naming conventions for proper system functionality.

## Project Structure

```
eleccion/
├── src/
│   └── funciones_streamlit/
│       ├── analizar_tipos_datos.py      # Data type analysis
│       ├── agregar_nombre_circuito.py  # Circuit name addition
│       ├── agregar_seccion.py          # Section addition
│       ├── crear_base_mesas.py         # Polling station database creation
│       ├── funciones.py                # Utility functions
│       ├── verificar_duplicados.py     # Duplicate verification
│       └── ...
├── streamlit/
│   ├── Inicio.py                       # Main application entry point
│   ├── pages/                          # Streamlit pages for different analyses
│   │   ├── 1_Diputados_y_Senadores.py
│   │   ├── 2_Concejales_municipales.py
│   │   ├── 3_Escuelas.py
│   │   └── 4_Electores.py
│   └── data/                           # Sample data files
├── utils/
│   ├── constantes.py                   # Application constants
│   └── data/                           # Processed data files
└── requirements.txt                    # Python dependencies
```

## Key Functions

### Data Analysis (`analizar_tipos_datos.py`)

- Analyzes data types in electoral CSV files
- Validates circuit codes, districts, polling stations, and institutions
- Provides normalization recommendations
- Creates normalized unique keys for data deduplication

### Data Processing Features

- **Circuit Code Normalization**: Removes leading zeros and standardizes format
- **District Processing**: Converts numeric districts to string format
- **Polling Station Validation**: Ensures consistent numbering format
- **Institution Name Standardization**: Normalizes school names used as polling places

## Data Validation

The system performs comprehensive validation including:

- Null value detection
- Data type consistency checks
- Duplicate record identification
- Format standardization
- Statistical analysis of voter counts

## Dependencies

- `streamlit>=1.28.0` - Web application framework
- `pandas>=2.0.0` - Data manipulation and analysis
- `matplotlib>=3.7.0` - Data visualization
- `numpy>=1.24.0` - Numerical computing
- `openpyxl>=3.1.0` - Excel file processing
- `python-dateutil>=2.8.2` - Date utilities

## Data Sources

The application is designed to work with official Argentine electoral data including:

- Electoral results by circuit and district
- Voter registration databases
- Polling station information
- Educational institution data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is intended for electoral data analysis and visualization purposes.

## Support

For technical support or questions about the electoral data processing system, please refer to the code documentation or create an issue in the repository.
