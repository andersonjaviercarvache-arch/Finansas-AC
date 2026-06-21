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
termino_busqueda = st.text_input("Ingresa el nombre, RUC, monto o número de comprobante a buscar")

# Lógica de procesamiento
if archivo_banco and archivo_sri:
    try:
        # 1. Lectura del Excel del Banco (Forzando formato texto desde el inicio)
        df_banco = pd.read_excel(archivo_banco, dtype=str)
        
        # 2. Lectura del TXT del SRI (Forzando formato texto desde el inicio)
        df_sri = pd.read_csv(archivo_sri, sep='\t', encoding='utf-8', dtype=str)
        
        if termino_busqueda:
            termino = termino_busqueda.upper()
            
            # 3. Filtrado de datos 
            # Reemplazamos los valores nulos (NaN) por texto vacío para evitar errores en la búsqueda
            df_banco = df_banco.fillna("")
            df_sri = df_sri.fillna("")

            filtro_banco = df_banco.apply(
                lambda x: x.str.upper().str.contains(termino, na=False)
            ).any(axis=1)
            resultados_banco = df_banco[filtro_banco]
            
            filtro_sri = df_sri.apply(
                lambda x: x.str.upper().str.contains(termino, na=False)
            ).any(axis=1)
            resultados_sri = df_sri[filtro_sri]
            
            # 4. Mostrar Resultados
            st.success(f"Resultados encontrados para: **{termino_busqueda}**")
            
            st.markdown("### Movimientos Bancarios")
            if not resultados_banco.empty:
                st.dataframe(resultados_banco, use_container_width=True)
            else:
                st.info("No se encontraron coincidencias en el estado de cuenta del banco.")
                
            st.markdown("### Comprobantes Electrónicos SRI")
            if not resultados_sri.empty:
                st.dataframe(resultados_sri, use_container_width=True)
            else:
                st.info("No se encontraron coincidencias en los comprobantes del SRI.")

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos. Detalle técnico: {e}")
else:
    st.warning("Por favor, sube ambos archivos para comenzar la conciliación.")
