import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Conciliación Contable Avanzada", layout="wide")
st.title("Sistema de Conciliación Contable")

# Función de normalización (Mantenida igual)
def normalizar_monto(val):
    val_str = str(val).strip()
    if not val_str or any(char in val_str for char in ['/', '-', '_', ':']):
        return None
    val_clean = val_str.replace("$", "").replace(" ", "")
    if "," in val_clean and "." in val_clean:
        val_clean = val_clean.replace(",", "")
    elif "," in val_clean:
        if len(val_clean.split(",")[-1]) == 2:
            val_clean = val_clean.replace(",", ".")
        else:
            val_clean = val_clean.replace(",", "")
    try:
        num = float(val_clean)
        return round(num, 2) if num > 0.01 else None
    except:
        return None

col_carga1, col_carga2 = st.columns(2)
with col_carga1:
    archivo_banco = st.file_uploader("Sube el estado de cuenta (Excel)", type=["xlsx", "xls"])
with col_carga2:
    archivo_sri = st.file_uploader("Sube los comprobantes SRI (TXT)", type=["txt"])

if archivo_banco and archivo_sri:
    try:
        df_banco = pd.read_excel(archivo_banco, dtype=str).fillna("")
        df_sri = pd.read_csv(archivo_sri, sep='\t', encoding='utf-8', dtype=str).fillna("")
        
        st.markdown("---")
        
        # --- Lógica de procesamiento (simplificada para legibilidad) ---
        # (Aquí va tu lógica de búsqueda previa del SRI que genera montos_sri_activos)
        # ... [Tu lógica original de búsqueda SRI aquí] ...
        
        # --- VISUALIZACIÓN ---
        st.subheader("Resultado de la Conciliación")
        
        # Asumiendo que resultados_banco ya está calculado:
        if 'resultados_banco' in locals() and not resultados_banco.empty:
            
            # Formato de estilo para la tabla
            def color_estado(val):
                color = 'green' if val == 'Facturado' else 'red'
                return f'color: {color}'

            # Mostrar tabla con formato
            st.dataframe(
                resultados_banco.style.map(color_estado, subset=['Estado SRI']),
                use_container_width=True
            )
            
            # Descarga
            csv_data = resultados_banco.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 Descargar Resultados", csv_data, "reporte_conciliado.csv", "text/csv")
        else:
            st.info("Realiza una búsqueda para ver los resultados aquí.")

    except Exception as e:
        st.error(f"Error: {e}")
