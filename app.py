import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Conciliación Contable Avanzada", layout="wide")
st.title("Sistema de Conciliación Contable")

# Función interna para normalizar y extraer montos numéricos de forma segura
def normalizar_monto(val):
    val_str = str(val).strip()
    # Evita procesar fechas, horas o claves de acceso como si fuesen montos
    if not val_str or any(char in val_str for char in ['/', '-', ':', '_']):
        return None
    
    # Limpieza de caracteres de moneda y espacios
    val_clean = val_str.replace("$", "").replace(" ", "")
    
    # Estandarización de puntos y comas decimales (común en formatos de Ecuador)
    if "," in val_clean and "." in val_clean:
        val_clean = val_clean.replace(",", "")
    elif "," in val_clean:
        if len(val_clean.split(",")[-1]) == 2:  # Ejemplo: 125,50 -> 125.50
            val_clean = val_clean.replace(",", ".")
        else:
            val_clean = val_clean.replace(",", "")
    
    try:
        num = float(val_clean)
        if num > 0.01:  # Ignora valores en cero o insignificantes
            return round(num, 2)
    except:
        pass
    return None

# Sección de carga de archivos
col_carga1, col_carga2 = st.columns(2)
with col_carga1:
    archivo_banco = st.file_uploader("Sube el estado de cuenta (Excel)", type=["xlsx", "xls"])
with col_carga2:
    archivo_sri = st.file_uploader("Sube los comprobantes SRI (TXT)", type=["txt"])

# Lógica principal de procesamiento
if archivo_banco and archivo_sri:
    try:
        # Lectura de archivos en formato texto plano para evitar errores de desbordamiento de dígitos
        df_banco = pd.read_excel(archivo_banco, dtype=str).fillna("")
        df_sri = pd.read_csv(archivo_sri, sep='\t', encoding='utf-8', dtype=str).fillna("")
        
        # Mapeo y extracción de todos los montos existentes en el documento del SRI
        montos_facturados_sri = set()
        for col in df_sri.columns:
            for val in df_sri[col]:
                m = normalizar_monto(val)
                if m is not None:
                    montos_facturados_sri.add(m)
        
        # Función para verificar si un movimiento bancario tiene un monto que coincida con el SRI
        def verificar_estado_facturacion(row):
            for val in row:
                m = normalizar_monto(val)
                if m is not None and m in montos_facturados_sri:
                    return "Facturado"
            return "Sin facturar"

        st.markdown("---")
        
        # Interfaz dividida para búsquedas independientes
        col_busqueda_banco, col_busqueda_sri = st.columns(2)
        
        # --- SECCIÓN: MOVIMIENTOS BANCARIOS ---
        with col_busqueda_banco:
            st.subheader("Búsqueda en Banco")
            termino_banco = st.text_input("Buscar en estado de cuenta (nombre, monto, descripción)")
            
            if termino_banco:
                termino_b = termino_banco.upper()
                filtro_banco = df_banco.apply(
                    lambda x: x.str.upper().str.contains(termino_b, na=False)
                ).any(axis=1)
                resultados_banco = df_banco[filtro_banco].copy()
                
                if not resultados_banco.empty:
                    # Aplicación de la lógica de coincidencia de valores facturados
                    resultados_banco['Estado SRI'] = resultados_banco.apply(verificar_estado_facturacion, axis=1)
                    
                    # Reorganización: Coloca la columna de estado al principio para validación visual rápida
                    cols_ordenadas = ['Estado SRI'] + [c for c in resultados_banco.columns if c != 'Estado SRI']
                    resultados_banco = resultados_banco[cols_ordenadas]
                    
                    # Conteo de registros para los cuadros numéricos
                    total_banco = len(resultados_banco)
                    facturados = len(resultados_banco[resultados_banco['Estado SRI'] == 'Facturado'])
                    sin_facturar = len(resultados_banco[resultados_banco['Estado SRI'] == 'Sin facturar'])
                    
                    # Cuadros de resultados en números (Métricas de Streamlit)
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Movimientos Encontrados", total_banco)
                    c2.metric("Facturados ✅", facturados)
                    c3.metric("Sin Facturar ❌", sin_facturar)
                    
                    # Despliegue de la tabla con montos y descripciones originales
                    st.dataframe(resultados_banco, use_container_width=True)
                else:
                    st.columns(1)[0].metric("Movimientos Encontrados", 0)
                    st.info("No se encontraron coincidencias en el banco.")
            else:
                st.caption("Vista previa del estado de cuenta (Incluye todas las columnas de montos)")
                st.dataframe(df_banco.head(5), use_container_width=True)
                
        # --- SECCIÓN: COMPROBANTES SRI ---
        with col_busqueda_sri:
            st.subheader("Búsqueda en SRI")
            termino_sri = st.text_input("Buscar en comprobantes (RUC, nombre, número de documento)")
            
            if termino_sri:
                termino_s = termino_sri.upper()
                filtro_sri = df_sri.apply(
                    lambda x: x.str.upper().str.contains(termino_s, na=False)
                ).any(axis=1)
                resultados_sri = df_sri[filtro_sri]
                
                if not resultados_sri.empty:
                    # Cuadro de resultados en números para el panel del SRI
                    st.columns(1)[0].metric("Comprobantes Encontrados", len(resultados_sri))
                    st.dataframe(resultados_sri, use_container_width=True)
                else:
                    st.columns(1)[0].metric("Comprobantes Encontrados", 0)
                    st.info("No se encontraron coincidencia en los registros del SRI.")
            else:
                st.caption("Vista previa de los comprobantes recibidos del SRI")
                st.dataframe(df_sri.head(5), use_container_width=True)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar la información. Detalle técnico: {e}")
else:
    st.warning("Por favor, sube ambos archivos para comenzar la conciliación.")
