import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Conciliación Contable Avanzada", layout="wide")
st.title("Sistema de Conciliación Contable")

def normalizar_monto(val):
    val_str = str(val).strip()
    
    # Descartar nulos, vacíos o marcadores de pandas (NaN)
    if not val_str or val_str.lower() in ['nan', 'nat', 'none', 'null']:
        return None
        
    # Si tiene letras, lo descartamos (evita procesar textos, nombres o descripciones)
    if re.search(r'[a-zA-Z]', val_str):
        return None
        
    # Descartar formatos de fecha, hora o códigos con múltiples guiones/barras
    if re.search(r'\d{2,4}[/-]\d{2,4}', val_str) or re.search(r'\d{2}:\d{2}', val_str) or val_str.count('-') > 1:
        return None
        
    # Limpiar espacios y símbolos de moneda
    val_clean = val_str.replace("$", "").replace(" ", "")
    
    # Debe contener al menos un dígito
    if not any(c.isdigit() for c in val_clean):
        return None
        
    # Asegurar que solo contenga dígitos, puntos, comas y un posible signo menos al inicio
    if not re.match(r'^-?[\d\.,]+$', val_clean):
        return None
        
    # Analizar inteligentemente puntos y comas para montos altos
    last_comma = val_clean.rfind(',')
    last_dot = val_clean.rfind('.')
    
    if last_comma > -1 and last_dot > -1:
        if last_comma > last_dot: 
            # Formato latino/europeo: 8.424,76
            val_clean = val_clean.replace(".", "").replace(",", ".")
        else: 
            # Formato americano: 8,424.76
            val_clean = val_clean.replace(",", "")
    elif last_comma > -1:
        # Si solo hay comas, comprobamos si la última es de decimales (1 o 2 dígitos al final)
        if len(val_clean) - last_comma - 1 <= 2: 
            val_clean = val_clean[:last_comma].replace(",", "") + "." + val_clean[last_comma+1:]
        else:
            val_clean = val_clean.replace(",", "")
    elif last_dot > -1:
        # Si hay más de un punto sin comas, son separadores de miles (ej. 1.000.000)
        if val_clean.count('.') > 1:
            val_clean = val_clean.replace(".", "")
            
    try:
        num = float(val_clean)
        # Usamos valor absoluto (abs) para emparejar cargos/abonos sin importar el signo
        if abs(num) > 0.00:
            return round(abs(num), 2)
    except ValueError:
        pass
        
    return None

col_carga1, col_carga2 = st.columns(2)
with col_carga1:
    archivos_banco = st.file_uploader(
        "Sube los estados de cuenta (Excel) [Máx. 6]", 
        type=["xlsx", "xls"], 
        accept_multiple_files=True
    )
with col_carga2:
    archivos_sri = st.file_uploader(
        "Sube los comprobantes SRI (TXT) [Máx. 6]", 
        type=["txt"], 
        accept_multiple_files=True
    )

# Límite de 6 archivos
if len(archivos_banco) > 6:
    st.warning("Has subido más de 6 archivos de banco. Solo se procesarán los primeros 6.")
    archivos_banco = archivos_banco[:6]

if len(archivos_sri) > 6:
    st.warning("Has subido más de 6 archivos del SRI. Solo se procesarán los primeros 6.")
    archivos_sri = archivos_sri[:6]

if archivos_banco and archivos_sri:
    try:
        # Concatenar archivos de banco
        lista_df_banco = []
        for archivo in archivos_banco:
            df_temp = pd.read_excel(archivo, dtype=str).fillna("")
            lista_df_banco.append(df_temp)
        df_banco = pd.concat(lista_df_banco, ignore_index=True)

        # Concatenar archivos SRI con el ajuste de codificación (latin1)
        lista_df_sri = []
        for archivo in archivos_sri:
            df_temp = pd.read_csv(
                archivo, 
                sep='\t', 
                encoding='latin1', 
                encoding_errors='replace', 
                dtype=str
            ).fillna("")
            lista_df_sri.append(df_temp)
        df_sri = pd.concat(lista_df_sri, ignore_index=True)
        
        st.markdown("---")
        
        col_busqueda_banco, col_busqueda_sri = st.columns(2)
        
        # --- SECCIÓN SRI ---
        with col_busqueda_sri:
            st.subheader("Búsqueda en SRI")
            termino_sri = st.text_input("1. Busca el comprobante (separa varias búsquedas con punto y coma ';')")
            
            if termino_sri:
                terminos_s = [re.escape(t.strip().upper()) for t in termino_sri.split(';') if t.strip()]
                patron_regex_s = '|'.join(terminos_s)
                
                filtro_sri = df_sri.apply(
                    lambda x: x.str.upper().str.contains(patron_regex_s, regex=True, na=False)
                ).any(axis=1)
                resultados_sri = df_sri[filtro_sri]
            else:
                resultados_sri = df_sri
                
            montos_sri_activos = []
            for col in resultados_sri.columns:
                for val in resultados_sri[col]:
                    m = normalizar_monto(val)
                    if m is not None:
                        montos_sri_activos.append(m)
            
            if termino_sri:
                if not resultados_sri.empty:
                    st.columns(1)[0].metric("Comprobantes Encontrados", len(resultados_sri))
                    st.dataframe(resultados_sri, use_container_width=True)
                else:
                    st.columns(1)[0].metric("Comprobantes Encontrados", 0)
                    st.info("No se encontraron coincidencias en el SRI.")
            else:
                st.caption("Vista previa de comprobantes")
                st.dataframe(df_sri.head(5), use_container_width=True)

        # --- SECCIÓN BANCO ---
        with col_busqueda_banco:
            st.subheader("Búsqueda en Banco")
            termino_banco = st.text_input("2. Busca en estado de cuenta (separa varias búsquedas con punto y coma ';')")
            
            if termino_banco:
                terminos_b = [re.escape(t.strip().upper()) for t in termino_banco.split(';') if t.strip()]
                patron_regex_b = '|'.join(terminos_b)
                
                filtro_banco = df_banco.apply(
                    lambda x: x.str.upper().str.contains(patron_regex_b, regex=True, na=False)
                ).any(axis=1)
                resultados_banco = df_banco[filtro_banco].copy()
                
                estados = []
                montos_detectados = []
                montos_disponibles = list(montos_sri_activos) 
                
                for idx, row in resultados_banco.iterrows():
                    encontrado = False
                    montos_en_fila = []
                    
                    for val in row:
                        m = normalizar_monto(val)
                        if m is not None:
                            montos_en_fila.append(m)
                    
                    for monto in montos_en_fila:
                        if monto in montos_disponibles:
                            montos_disponibles.remove(monto) 
                            estados.append("Facturado")
                            montos_detectados.append(monto)
                            encontrado = True
                            break 
                    
                    if not encontrado:
                        estados.append("Sin facturar")
                        montos_detectados.append(montos_en_fila[0] if montos_en_fila else 0.0)

                if not resultados_banco.empty:
                    resultados_banco['Estado SRI'] = estados
                    resultados_banco['Monto Detectado'] = montos_detectados
                    
                    cols_ordenadas = ['Estado SRI', 'Monto Detectado'] + [c for c in resultados_banco.columns if c not in ['Estado SRI', 'Monto Detectado']]
                    resultados_banco = resultados_banco[cols_ordenadas]
                    
                    suma_facturados = resultados_banco[resultados_banco['Estado SRI'] == 'Facturado']['Monto Detectado'].sum()
                    suma_sin_facturar = resultados_banco[resultados_banco['Estado SRI'] == 'Sin facturar']['Monto Detectado'].sum()
                    
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Resultados", len(resultados_banco))
                    c2.metric("Suma Facturada ✅", f"${suma_facturados:,.2f}")
                    c3.metric("Suma Sin Facturar ❌", f"${suma_sin_facturar:,.2f}")
                    
                    # Se muestra la tabla en pantalla
                    st.dataframe(resultados_banco, use_container_width=True)
                    
                    # --- FUNCIÓN DE DESCARGA ---
                    csv_data = resultados_banco.to_csv(index=False).encode('utf-8-sig')
                    
                    st.download_button(
                        label="📥 Descargar Tabla de Resultados (Excel/CSV)",
                        data=csv_data,
                        file_name="reporte_banco_conciliado.csv",
                        mime="text/csv",
                        help="Haz clic aquí para guardar los resultados de tu búsqueda con sus montos, fechas y estados."
                    )
                    
                else:
                    st.columns(1)[0].metric("Resultados", 0)
                    st.info("No se encontraron coincidencias en el banco.")
            else:
                st.caption("Vista previa del estado de cuenta")
                st.dataframe(df_banco.head(5), use_container_width=True)

    except Exception as e:
        st.error(f"Ocurrió un error al procesar la información. Detalle técnico: {e}")
else:
    st.warning("Por favor, sube al menos un archivo en ambas secciones para comenzar la conciliación.")
