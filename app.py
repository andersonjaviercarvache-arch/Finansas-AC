import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Conciliación Contable", layout="wide")
st.title("Sistema de Conciliación Contable")

# Sección de carga de archivos
col1, col2 = st.columns(2)
with col1:
    archivo_banco = st.file_uploader("Sube el estado de cuenta (Excel)", type=["xlsx", "xls"])
with col2:
    archivo_sri = st.file_uploader("Sube los comprobantes SRI (TXT)", type=["txt"])

# Barra de búsqueda
st.subheader("Búsqueda de Movimientos")
termino_busqueda = st.text_input("Ingresa el nombre del cliente, proveedor o detalle a buscar")

# Lógica de procesamiento
if archivo_banco and archivo_sri:
    try:
        # 1. Lectura del Excel del Banco
        # Asume que la cabecera está en la primera fila. Ajusta 'header' si es distinto.
        df_banco = pd.read_excel(archivo_banco)
        
        # 2. Lectura del TXT del SRI
        # El SRI suele separar los datos por tabulaciones ('\t') en sus reportes de texto.
        df_sri = pd.read_csv(archivo_sri, sep='\t', encoding='utf-8')
        
        if termino_busqueda:
            # 3. Filtrado de datos
            # Convierte todo a mayúsculas para que la búsqueda no sea sensible a minúsculas/mayúsculas
            termino = termino_busqueda.upper()
            
            # Filtra el DataFrame del banco (ajusta 'CONCEPTO' o 'DETALLE' según la columna de tu banco)
            # Reemplaza 'Descripcion' con el nombre real de la columna de tu Excel
            columnas_banco_str = df_banco.select_dtypes(include=['object']).columns
            filtro_banco = df_banco[columnas_banco_str].apply(lambda x: x.str.upper().str.contains(termino, na=False)).any(axis=1)
            resultados_banco = df_banco[filtro_banco]
            
            # Filtra el DataFrame del SRI (buscará en columnas como 'Razón Social Proveedor')
            columnas_sri_str = df_sri.select_dtypes(include=['object']).columns
            filtro_sri = df_sri[columnas_sri_str].apply(lambda x: x.str.upper().str.contains(termino, na=False)).any(axis=1)
            resultados_sri = df_sri[filtro_sri]
            
            # 4. Mostrar Resultados
            st.success(f"Resultados encontrados para: **{termino_busqueda}**")
            
            st.markdown("### Movimientos Bancarios")
            if not resultados_banco.empty:
                st.dataframe(resultados_banco, use_container_width=True)
            else:
                st.info("No se encontraron coincidencias en el estado de cuenta.")
                
            st.markdown("### Comprobantes Electrónicos SRI")
            if not resultados_sri.empty:
                st.dataframe(resultados_sri, use_container_width=True)
            else:
                st.info("No se encontraron coincidencias en los comprobantes del SRI.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos. Revisa el formato. Detalle técnico: {e}")
else:
    st.warning("Por favor, sube ambos archivos para comenzar la conciliación.")
