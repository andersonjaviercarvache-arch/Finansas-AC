import streamlit as st
import pandas as pd

# Configuracion de la pagina
st.set_page_config(page_title="Conciliación Contable", layout="wide")
st.title("Sistema de Conciliación Contable")

# Seccion de carga de archivos
col_carga1, col_carga2 = st.columns(2)
with col_carga1:
    archivo_banco = st.file_uploader("Sube el estado de cuenta (Excel)", type=["xlsx", "xls"])
with col_carga2:
    archivo_sri = st.file_uploader("Sube los comprobantes SRI (TXT)", type=["txt"])

# Logica de procesamiento
if archivo_banco and archivo_sri:
    try:
        # Lectura de archivos forzando formato texto
        df_banco = pd.read_excel(archivo_banco, dtype=str).fillna("")
        df_sri = pd.read_csv(archivo_sri, sep='\t', encoding='utf-8', dtype=str).fillna("")
        
        st.markdown("---")
        
        # Separamos la interfaz en dos grandes bloques para buscar por separado
        col_busqueda_banco, col_busqueda_sri = st.columns(2)
        
        # Bloque del Banco
        with col_busqueda_banco:
            st.subheader("Búsqueda en Banco")
            termino_banco = st.text_input("Buscar en estado de cuenta (nombre, monto, etc.)")
            
            if termino_banco:
                termino_b = termino_banco.upper()
                filtro_banco = df_banco.apply(
                    lambda x: x.str.upper().str.contains(termino_b, na=False)
                ).any(axis=1)
                resultados_banco = df_banco[filtro_banco]
                
                if not resultados_banco.empty:
                    st.success(f"Resultados para **{termino_banco}**")
                    st.dataframe(resultados_banco, use_container_width=True)
                else:
                    st.info("No se encontraron coincidencias en el banco.")
            else:
                # Opcional Muestra una vista previa de los datos si no hay busqueda activa
                st.caption("Vista previa del estado de cuenta")
                st.dataframe(df_banco.head(5), use_container_width=True)
                
        # Bloque del SRI
        with col_busqueda_sri:
            st.subheader("Búsqueda en SRI")
            termino_sri = st.text_input("Buscar en comprobantes (RUC, nombre, clave, etc.)")
            
            if termino_sri:
                termino_s = termino_sri.upper()
                filtro_sri = df_sri.apply(
                    lambda x: x.str.upper().str.contains(termino_s, na=False)
                ).any(axis=1)
                resultados_sri = df_sri[filtro_sri]
                
                if not resultados_sri.empty:
                    st.success(f"Resultados para **{termino_sri}**")
                    st.dataframe(resultados_sri, use_container_width=True)
                else:
                    st.info("No se encontraron coincidencias en el SRI.")
            else:
                # Opcional Muestra una vista previa de los datos si no hay busqueda activa
                st.caption("Vista previa de los comprobantes")
                st.dataframe(df_sri.head(5), use_container_width=True)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar los archivos. Detalle técnico {e}")
else:
    st.warning("Por favor, sube ambos archivos para comenzar la conciliación.")
