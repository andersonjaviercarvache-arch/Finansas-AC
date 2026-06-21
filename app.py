import streamlit as st
import pandas as pd

st.set_page_config(page_title="Conciliación Contable Avanzada", layout="wide")
st.title("Sistema de Conciliación Contable")

def normalizar_monto(val):
    val_str = str(val).strip()
    if not val_str or any(char in val_str for char in ['/', '-', '_']):
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
        if num > 0.01:
            return round(num, 2)
    except:
        pass
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
        
        col_busqueda_banco, col_busqueda_sri = st.columns(2)
        
        # SECCION SRI (Procesamos esto primero para saber qué montos buscar)
        with col_busqueda_sri:
            st.subheader("Búsqueda en SRI")
            termino_sri = st.text_input("1. Busca el comprobante (RUC, nombre...)")
            
            if termino_sri:
                termino_s = termino_sri.upper()
                filtro_sri = df_sri.apply(lambda x: x.str.upper().str.contains(termino_s, na=False)).any(axis=1)
                resultados_sri = df_sri[filtro_sri]
            else:
                resultados_sri = df_sri
                
            montos_sri_activos = set()
            for col in resultados_sri.columns:
                for val in resultados_sri[col]:
                    m = normalizar_monto(val)
                    if m is not None:
                        montos_sri_activos.add(m)
            
            if termino_sri:
                if not resultados_sri.empty:
                    st.columns(1)[0].metric("Comprobantes Encontrados", len(resultados_sri))
                    st.dataframe(resultados_sri, use_container_width=True)
                else:
                    st.info("No se encontraron coincidencias en el SRI.")
            else:
                st.caption("Vista previa de comprobantes")
                st.dataframe(df_sri.head(5), use_container_width=True)

        # SECCION BANCO
        with col_busqueda_banco:
            st.subheader("Búsqueda en Banco")
            termino_banco = st.text_input("2. Busca en estado de cuenta (nombre, detalle...)")
            
            if termino_banco:
                termino_b = termino_banco.upper()
                filtro_banco = df_banco.apply(lambda x: x.str.upper().str.contains(termino_b, na=False)).any(axis=1)
                resultados_banco = df_banco[filtro_banco].copy()
                
                def evaluar_fila(row):
                    montos_en_fila = []
                    for val in row:
                        m = normalizar_monto(val)
                        if m is not None:
                            montos_en_fila.append(m)
                    
                    for monto in montos_en_fila:
                        if monto in montos_sri_activos:
                            return pd.Series(["Facturado", monto])
                    
                    monto_sin_facturar = montos_en_fila[0] if montos_en_fila else 0.0
                    return pd.Series(["Sin facturar", monto_sin_facturar])

                if not resultados_banco.empty:
                    resultados_banco[['Estado SRI', 'Monto Detectado']] = resultados_banco.apply(evaluar_fila, axis=1)
                    
                    cols_ordenadas = ['Estado SRI', 'Monto Detectado'] + [c for c in resultados_banco.columns if c not in ['Estado SRI', 'Monto Detectado']]
                    resultados_banco = resultados_banco[cols_ordenadas]
                    
                    suma_facturados = resultados_banco[resultados_banco['Estado SRI'] == 'Facturado']['Monto Detectado'].sum()
                    suma_sin_facturar = resultados_banco[resultados_banco['Estado SRI'] == 'Sin facturar']['Monto Detectado'].sum()
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Resultados", len(resultados_banco))
                    c2.metric("Suma Facturada ✅", f"${suma_facturados:,.2f}")
                    c3.metric("Suma Sin Facturar ❌", f"${suma_sin_facturar:,.2f}")
                    
                    st.dataframe(resultados_banco, use_container_width=True)
                else:
                    st.info("No se encontraron coincidencias en el banco.")
            else:
                st.caption("Vista previa del estado de cuenta")
                st.dataframe(df_banco.head(5), use_container_width=True)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar la información. Detalle técnico {e}")
else:
    st.warning("Por favor, sube ambos archivos para comenzar la conciliación.")
