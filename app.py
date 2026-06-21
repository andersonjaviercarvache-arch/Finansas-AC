import streamlit as st
import pandas as pd
import re
from fpdf import FPDF

# Configuración de página
st.set_page_config(page_title="Sistema de Conciliación Contable", layout="wide")
st.title("Sistema de Conciliación Contable Avanzada")

# Función para limpiar y normalizar montos
def normalizar_monto(val):
    val_str = str(val).strip()
    if not val_str or any(char in val_str for char in ['/', '-', '_', ':']):
        return None
    val_clean = val_str.replace("$", "").replace(" ", "").replace(",", "")
    try:
        num = float(val_clean)
        return round(num, 2) if num > 0.01 else None
    except:
        return None

# Función para generar el PDF
def generar_pdf(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Reporte de Conciliacion Bancaria", ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", size=8)
    # Encabezados
    col_width = 35
    row_height = 8
    for col in df.columns:
        pdf.cell(col_width, row_height, str(col), border=1)
    pdf.ln()
    
    # Filas
    for _, row in df.iterrows():
        for col in df.columns:
            pdf.cell(col_width, row_height, str(row[col]), border=1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1')

# Interfaz de carga
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
        col_busqueda_banco, col_busqueda_sri = st.columns(2)
        
        # Procesamiento SRI
        with col_busqueda_sri:
            st.subheader("Búsqueda en SRI")
            termino_sri = st.text_input("1. Busca el comprobante (separa con ';')")
            if termino_sri:
                patron = '|'.join([re.escape(t.strip().upper()) for t in termino_sri.split(';') if t.strip()])
                filtro_sri = df_sri.apply(lambda x: x.str.upper().str.contains(patron, regex=True, na=False)).any(axis=1)
                resultados_sri = df_sri[filtro_sri]
            else:
                resultados_sri = df_sri
            
            montos_sri_activos = [m for col in resultados_sri.columns for m in [normalizar_monto(v) for v in resultados_sri[col]] if m is not None]

        # Procesamiento Banco
        with col_busqueda_banco:
            st.subheader("Búsqueda en Banco")
            termino_banco = st.text_input("2. Busca en banco (separa con ';')")
            if termino_banco:
                patron_b = '|'.join([re.escape(t.strip().upper()) for t in termino_banco.split(';') if t.strip()])
                filtro_banco = df_banco.apply(lambda x: x.str.upper().str.contains(patron_b, regex=True, na=False)).any(axis=1)
                resultados_banco = df_banco[filtro_banco].copy()
                
                estados, montos_detectados = [], []
                disponibles = list(montos_sri_activos)
                
                for _, row in resultados_banco.iterrows():
                    m_fila = [m for val in row if (m := normalizar_monto(val)) is not None]
                    encontrado = False
                    for m in m_fila:
                        if m in disponibles:
                            disponibles.remove(m)
                            estados.append("Facturado")
                            montos_detectados.append(m)
                            encontrado = True
                            break
                    if not encontrado:
                        estados.append("Sin facturar")
                        montos_detectados.append(m_fila[0] if m_fila else 0.0)

                resultados_banco['Estado SRI'] = estados
                resultados_banco['Monto Detectado'] = montos_detectados
                
                # Métricas
                c1, c2, c3 = st.columns(3)
                c1.metric("Transacciones", len(resultados_banco))
                c2.metric("Facturado", f"${resultados_banco[resultados_banco['Estado SRI']=='Facturado']['Monto Detectado'].sum():,.2f}")
                c3.metric("Sin Facturar", f"${resultados_banco[resultados_banco['Estado SRI']=='Sin facturar']['Monto Detectado'].sum():,.2f}")
                
                st.dataframe(resultados_banco, use_container_width=True)
                
                # Botón Descarga PDF
                st.download_button(
                    label="📥 Descargar Reporte en PDF",
                    data=generar_pdf(resultados_banco),
                    file_name="reporte_conciliacion.pdf",
                    mime="application/pdf"
                )
    except Exception as e:
        st.error(f"Error procesando archivos: {e}")
else:
    st.warning("Por favor, sube los archivos de Excel (Banco) y TXT (SRI).")
