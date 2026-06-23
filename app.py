import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import datetime

st.set_page_config(page_title="Gestor de Rentabilidad", layout="wide")

st.title("📊 Gestor Financiero - Latitud Solar")

# --- INICIALIZAR MEMORIA ---
if 'proyectos' not in st.session_state:
    st.session_state.proyectos = []

# Diccionario para traducir los meses
meses_es = {1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio", 
            7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"}

# --- SECCIÓN: REGISTRO DE PROYECTO ---
st.header("Registrar Nuevo Proyecto")

col_info, col_dias, col_fecha = st.columns([2, 1, 1])
nombre_proyecto = col_info.text_input("Nombre del Proyecto")
dias_trabajo = col_dias.number_input("Días de Obra (Personal)", min_value=1, value=4)
fecha_proyecto = col_fecha.date_input("Fecha del Proyecto", value=datetime.date.today())

st.write("---")

st.subheader("1. Costos de Personal (Por Día)")
st.write("Edita la tarifa o marca la casilla 'Asignado' para incluir al trabajador en esta obra.")

df_personal_base = pd.DataFrame([
    {"Rol": "Supervisor", "Costo Día ($)": 50.00, "Asignado": True},
    {"Rol": "Técnico 1", "Costo Día ($)": 37.50, "Asignado": True},
    {"Rol": "Técnico 2", "Costo Día ($)": 37.50, "Asignado": True},
    {"Rol": "Ayudante", "Costo Día ($)": 25.00, "Asignado": False}
])
df_personal_editado = st.data_editor(df_personal_base, use_container_width=True, hide_index=True)

st.write("---")

# --- SECCIÓN DE VIÁTICOS INDEPENDIENTES (CON HOSPEDAJE) ---
st.subheader("2. Desglose de Viáticos (Por Persona)")
st.write("Ingresa el valor diario y cuántos días aplica cada rubro.")

col_v1, col_v2, col_v3, col_v4 = st.columns(4)

with col_v1:
    st.markdown("**Alimentación**")
    alim_costo = st.number_input("Costo/Día ($)", min_value=0.0, value=15.0, key="alim_c")
    alim_dias = st.number_input("Días", min_value=0, value=dias_trabajo, key="alim_d")

with col_v2:
    st.markdown("**Movilización**")
    mov_costo = st.number_input("Costo/Día ($)", min_value=0.0, value=15.0, key="mov_c")
    mov_dias = st.number_input("Días", min_value=0, value=dias_trabajo, key="mov_d")

with col_v3:
    st.markdown("**Hidratación**")
    hidra_costo = st.number_input("Costo/Día ($)", min_value=0.0, value=10.0, key="hidra_c")
    hidra_dias = st.number_input("Días", min_value=0, value=dias_trabajo, key="hidra_d")

with col_v4:
    st.markdown("**Hospedaje**")
    hosp_costo = st.number_input("Costo/Noche ($)", min_value=0.0, value=20.0, key="hosp_c")
    hosp_dias = st.number_input("Noches", min_value=0, value=max(0, dias_trabajo - 1), key="hosp_d")

total_alim_pp = alim_costo * alim_dias
total_mov_pp = mov_costo * mov_dias
total_hidra_pp = hidra_costo * hidra_dias
total_hosp_pp = hosp_costo * hosp_dias

viatico_total_pp = total_alim_pp + total_mov_pp + total_hidra_pp + total_hosp_pp
st.info(f"**Total acumulado de viáticos por cada persona:** ${viatico_total_pp:.2f}")

st.write("---")

st.subheader("3. Materiales y Otros")
costo_materiales = st.number_input("Costo de Materiales o Equipos ($)", min_value=0.0, value=0.0, step=50.0)

st.write("---")

# --- CÁLCULO DE MÁRGENES Y PRECIO FINAL EDITABLE ---
st.subheader("4. Ajuste de Márgenes y Precio de Venta")

col_pct1, col_pct2 = st.columns(2)
pct_imprevistos = col_pct1.slider("Porcentaje para Imprevistos (%)", min_value=0, max_value=100, value=20, step=5)
pct_ganancia_sugerida = col_pct2.slider("Porcentaje de Ganancia Esperada (%)", min_value=0, max_value=100, value=40, step=5)

personal_activo = df_personal_editado[df_personal_editado["Asignado"] == True]
num_personas = len(personal_activo)

costo_mano_obra = personal_activo["Costo Día ($)"].sum() * dias_trabajo
costo_viaticos_total = viatico_total_pp * num_personas
costo_directo = costo_mano_obra + costo_viaticos_total + costo_materiales

reserva_imprevistos = costo_directo * (pct_imprevistos / 100)
ganancia_calculada = costo_directo * (pct_ganancia_sugerida / 100)

precio_sugerido = costo_directo + reserva_imprevistos + ganancia_calculada

st.markdown("### 🎯 Definir Precio Final")
st.info(f"💡 El precio base sugerido es de **${precio_sugerido:,.2f}**.")

precio_venta_final = st.number_input(
    "Ingresa el Precio de Venta a Cobrar (Sin IVA) ($)", 
    min_value=0.0, 
    value=float(precio_sugerido), 
    step=10.0
)

ganancia_real = precio_venta_final - costo_directo - reserva_imprevistos
iva_monto = precio_venta_final * 0.15
precio_total_con_iva = precio_venta_final + iva_monto

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
col_s1.metric("Costo Directo", f"${costo_directo:,.2f}")
col_s2.metric(f"Imprevistos ({pct_imprevistos}%)", f"${reserva_imprevistos:,.2f}")
col_s3.metric("Ganancia Neta", f"${ganancia_real:,.2f}")
col_s4.metric("PRECIO DE VENTA FINAL", f"${precio_venta_final:,.2f}")

st.success(f"**PRECIO DE VENTA FINAL:** ${precio_venta_final:,.2f}  |  **IVA (15%):** ${iva_monto:,.2f}  |  **PRECIO TOTAL:** ${precio_total_con_iva:,.2f}")

if st.button("Guardar Proyecto en el Mes", type="primary"):
    if nombre_proyecto:
        nombres_existentes = [p["Proyecto"] for p in st.session_state.proyectos]
        if nombre_proyecto in nombres_existentes:
            st.error("Ya existe un proyecto con este nombre. Por favor, usa un nombre distinto.")
        else:
            mes_str = meses_es[fecha_proyecto.month]
            st.session_state.proyectos.append({
                "Fecha": fecha_proyecto.strftime("%Y-%m-%d"),
                "Mes": mes_str,
                "Año": fecha_proyecto.year,
                "Proyecto": nombre_proyecto,
                "Costo Directo": costo_directo,
                "Fondo Imprevistos": reserva_imprevistos, 
                "Ganancia Neta": ganancia_real,           
                "PRECIO VENTA FINAL": precio_venta_final,
                "IVA (15%)": iva_monto,
                "PRECIO TOTAL": precio_total_con_iva,
                "_Dias": dias_trabajo,
                "_Personal": personal_activo.to_dict('records'),
                "_Viaticos": {
                    "Alimentación": {"costo": alim_costo, "dias": alim_dias},
                    "Movilización": {"costo": mov_costo, "dias": mov_dias},
                    "Hidratación": {"costo": hidra_costo, "dias": hidra_dias},
                    "Hospedaje": {"costo": hosp_costo, "dias": hosp_dias}
                },
                "_Materiales": costo_materiales
            })
            st.success(f"Proyecto '{nombre_proyecto}' registrado exitosamente en {mes_str} {fecha_proyecto.year}.")
            st.rerun()
    else:
        st.error("Por favor, ingresa el nombre del proyecto.")

# --- SECCIÓN: REPORTE MENSUAL Y DESCARGAS ---
st.write("---")
st.header("Reporte de Proyectos y Cotizaciones")

if st.session_state.proyectos:
    # 1. Mostrar Tabla General
    datos_publicos = [{k: v for k, v in p.items() if not k.startswith("_")} for p in st.session_state.proyectos]
    df_resultados = pd.DataFrame(datos_publicos)
    df_resultados.fillna(0, inplace=True)
    
    # Reordenar columnas para que la tabla sea fácil de leer
    columnas_ordenadas = ["Fecha", "Mes", "Proyecto", "Costo Directo", "Fondo Imprevistos", "Ganancia Neta", "PRECIO VENTA FINAL", "IVA (15%)", "PRECIO TOTAL"]
    df_resultados = df_resultados[[col for col in columnas_ordenadas if col in df_resultados.columns]]
    
    formato_moneda = {col: "${:,.2f}" for col in df_resultados.columns if col not in ["Fecha", "Mes", "Proyecto", "Año"]}
    df_mostrar = df_resultados.style.format(formato_moneda)
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    
    # 2. Panel de Gestión (Eliminar y Descargar)
    st.write("---")
    st.subheader("🛠️ Panel de Control y Exportación")
    col_gest1, col_gest2 = st.columns(2)
    
    with col_gest1:
        st.markdown("**❌ Eliminar un Proyecto**")
        nombres_proyectos = [p["Proyecto"] for p in st.session_state.proyectos]
        proyecto_a_eliminar = st.selectbox("Selecciona el proyecto que deseas borrar:", nombres_proyectos)
        
        if st.button("Eliminar Proyecto Seleccionado"):
            st.session_state.proyectos = [p for p in st.session_state.proyectos if p["Proyecto"] != proyecto_a_eliminar]
            st.warning(f"El proyecto '{proyecto_a_eliminar}' ha sido eliminado.")
            st.rerun()

    # --- LÓGICA DE EXPORTACIÓN A PDF (DINÁMICA Y FILTRADA) ---
    def generar_pdf(lista_proyectos, df_interno, tipo_exportacion, titulo_reporte=None):
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.set_margins(left=10, top=15, right=10)
        pdf.add_page() 
        
        if tipo_exportacion == "individual":
            # ==========================================
            # 1. COTIZACIÓN CLIENTE (Solo individual)
            # ==========================================
            pdf.set_font("Helvetica", 'B', 14)
            pdf.cell(0, 8, "COTIZACIÓN COMERCIAL - LATITUD SOLAR", new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(5)
            
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(85, 8, "Descripción del Proyecto", border=1, align='C')
            pdf.cell(35, 8, "Subtotal", border=1, align='C')
            pdf.cell(35, 8, "IVA (15%)", border=1, align='C')
            pdf.cell(35, 8, "Total a Pagar", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
            
            pdf.set_font("Helvetica", '', 9)
            for _, row in df_interno.iterrows():
                nombre = str(row['Proyecto'])[:40]
                pdf.cell(85, 8, nombre, border=1)
                pdf.cell(35, 8, f"${row['PRECIO VENTA FINAL']:,.2f}", border=1, align='R')
                pdf.cell(35, 8, f"${row['IVA (15%)']:,.2f}", border=1, align='R')
                pdf.cell(35, 8, f"${row['PRECIO TOTAL']:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align='R')
                
            pdf.ln(3)
            pdf.set_font("Helvetica", 'I', 8)
            pdf.cell(0, 8, "Nota: Los valores incluyen mano de obra, viáticos y equipos acordados.", new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(10)

            # ==========================================
            # 2. DESGLOSE DETALLADO DE COSTOS (Solo individual)
            # ==========================================
            pdf.set_font("Helvetica", 'B', 14)
            pdf.cell(0, 8, "DESGLOSE DETALLADO DE COSTOS OPERATIVOS", new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(5)

            for p in lista_proyectos:
                pdf.set_font("Helvetica", 'B', 10)
                pdf.cell(0, 8, f"Proyecto: {p['Proyecto']} (Fecha: {p['Fecha']} | Duración: {p['_Dias']} días)", new_x="LMARGIN", new_y="NEXT", align='L')
                
                # Tabla Personal
                pdf.set_font("Helvetica", 'B', 9)
                pdf.cell(0, 6, "Costo de Personal (Asignado a la obra):", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(70, 6, "Rol", border=1)
                pdf.cell(60, 6, "Costo Diario por Persona", border=1, align='C')
                pdf.cell(60, 6, "Total Rol", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
                
                pdf.set_font("Helvetica", '', 9)
                suma_personal = 0
                for persona in p["_Personal"]:
                    total_rol = persona["Costo Día ($)"] * p["_Dias"]
                    suma_personal += total_rol
                    pdf.cell(70, 6, str(persona["Rol"]), border=1)
                    pdf.cell(60, 6, f"${persona['Costo Día ($)']:,.2f}", border=1, align='C')
                    pdf.cell(60, 6, f"${total_rol:,.2f}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
                
                pdf.set_font("Helvetica", 'B', 9)
                pdf.cell(130, 6, "TOTAL COSTO PERSONAL", border=1, align='R')
                pdf.cell(60, 6, f"${suma_personal:,.2f}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
                pdf.ln(3)
                
                # Tabla Viáticos
                pdf.set_font("Helvetica", 'B', 9)
                pdf.cell(0, 6, "Desglose de Viáticos (Todo el personal asignado):", new_x="LMARGIN", new_y="NEXT")
                pdf.cell(60, 6, "Concepto", border=1)
                pdf.cell(40, 6, "Diario/Noche", border=1, align='C')
                pdf.cell(30, 6, "Días", border=1, align='C')
                pdf.cell(60, 6, "Total Grupo", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
                
                pdf.set_font("Helvetica", '', 9)
                num_personas = len(p["_Personal"])
                suma_viaticos = 0
                for concepto, datos in p["_Viaticos"].items():
                    total_concepto = datos["costo"] * datos["dias"] * num_personas
                    suma_viaticos += total_concepto
                    pdf.cell(60, 6, concepto, border=1)
                    pdf.cell(40, 6, f"${datos['costo']:,.2f}", border=1, align='C')
                    pdf.cell(30, 6, str(datos['dias']), border=1, align='C')
                    pdf.cell(60, 6, f"${total_concepto:,.2f}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
                    
                pdf.set_font("Helvetica", 'B', 9)
                pdf.cell(130, 6, "TOTAL VIÁTICOS", border=1, align='R')
                pdf.cell(60, 6, f"${suma_viaticos:,.2f}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
                pdf.ln(3)
                
                pdf.set_font("Helvetica", '', 9)
                pdf.cell(0, 6, f"Materiales y Otros Costos: ${p['_Materiales']:,.2f}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(8)
                
            # ==========================================
            # 3. REPORTE INTERNO (Individual)
            # ==========================================
            pdf.ln(2)
            pdf.set_font("Helvetica", 'B', 14)
            pdf.cell(0, 8, "REPORTE INTERNO DE RENTABILIDAD", new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(5)
            
            pdf.set_font("Helvetica", 'B', 8)
            pdf.cell(50, 8, "Proyecto", border=1, align='C')
            pdf.cell(35, 8, "Costo Directo", border=1, align='C')
            pdf.cell(35, 8, "Imprevistos", border=1, align='C')
            pdf.cell(35, 8, "Ganancia Neta", border=1, align='C')
            pdf.cell(35, 8, "Precio Venta", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
            
            pdf.set_font("Helvetica", '', 8)
            for _, row in df_interno.iterrows():
                nombre = str(row['Proyecto'])[:25]
                pdf.cell(50, 8, nombre, border=1)
                pdf.cell(35, 8, f"${row.get('Costo Directo', 0.0):,.2f}", border=1, align='R')
                pdf.cell(35, 8, f"${row.get('Fondo Imprevistos', 0.0):,.2f}", border=1, align='R')
                pdf.cell(35, 8, f"${row.get('Ganancia Neta', 0.0):,.2f}", border=1, align='R')
                pdf.cell(35, 8, f"${row.get('PRECIO VENTA FINAL', 0.0):,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align='R')

        elif tipo_exportacion == "todos":
            # ==========================================
            # REPORTE GENERAL (Consolidado por Mes)
            # ==========================================
            pdf.set_font("Helvetica", 'B', 14)
            pdf.cell(0, 8, titulo_reporte, new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(5)
            
            # Encabezados ajustados a 190mm (40 + 25x6 = 190)
            pdf.set_font("Helvetica", 'B', 8)
            pdf.cell(40, 8, "Proyecto", border=1, align='C')
            pdf.cell(25, 8, "Costo Dir.", border=1, align='C')
            pdf.cell(25, 8, "Imprev.", border=1, align='C')
            pdf.cell(25, 8, "Ganancia", border=1, align='C')
            pdf.cell(25, 8, "IVA (15%)", border=1, align='C')
            pdf.cell(25, 8, "Venta Final", border=1, align='C')
            pdf.cell(25, 8, "Precio Total", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
            
            pdf.set_font("Helvetica", '', 8)
            
            sum_costo = sum_imprev = sum_ganancia = sum_iva = sum_venta = sum_total = 0
            
            for _, row in df_interno.iterrows():
                nombre = str(row['Proyecto'])[:20]
                c_directo = row.get('Costo Directo', 0.0)
                c_imprevisto = row.get('Fondo Imprevistos', 0.0)
                c_ganancia = row.get('Ganancia Neta', 0.0)
                iva = row.get('IVA (15%)', 0.0)
                p_venta = row.get('PRECIO VENTA FINAL', 0.0)
                p_total = row.get('PRECIO TOTAL', 0.0)
                
                sum_costo += c_directo
                sum_imprev += c_imprevisto
                sum_ganancia += c_ganancia
                sum_iva += iva
                sum_venta += p_venta
                sum_total += p_total
                
                pdf.cell(40, 8, nombre, border=1)
                pdf.cell(25, 8, f"${c_directo:,.2f}", border=1, align='R')
                pdf.cell(25, 8, f"${c_imprevisto:,.2f}", border=1, align='R')
                pdf.cell(25, 8, f"${c_ganancia:,.2f}", border=1, align='R')
                pdf.cell(25, 8, f"${iva:,.2f}", border=1, align='R')
                pdf.cell(25, 8, f"${p_venta:,.2f}", border=1, align='R')
                pdf.cell(25, 8, f"${p_total:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align='R')
                
            # Fila de Totales Generales
            pdf.set_font("Helvetica", 'B', 8)
            pdf.cell(40, 8, "TOTALES MENSUALES", border=1, align='R')
            pdf.cell(25, 8, f"${sum_costo:,.2f}", border=1, align='R')
            pdf.cell(25, 8, f"${sum_imprev:,.2f}", border=1, align='R')
            pdf.cell(25, 8, f"${sum_ganancia:,.2f}", border=1, align='R')
            pdf.cell(25, 8, f"${sum_iva:,.2f}", border=1, align='R')
            pdf.cell(25, 8, f"${sum_venta:,.2f}", border=1, align='R')
            pdf.cell(25, 8, f"${sum_total:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align='R')

        temp_file = "temp_report.pdf"
        pdf.output(temp_file)
        with open(temp_file, "rb") as f:
            pdf_bytes = f.read()
        os.remove(temp_file)
        return pdf_bytes

    with col_gest2:
        st.markdown("**📥 Descargar PDF**")
        opciones_descarga = ["Todos los proyectos (Por Mes)"] + nombres_proyectos
        seleccion_descarga = st.selectbox("Selecciona qué deseas exportar al PDF:", opciones_descarga)
        
        if seleccion_descarga == "Todos los proyectos (Por Mes)":
            # Extraer meses únicos que tienen proyectos registrados para no mostrar meses vacíos
            meses_disponibles = list(set([p["Mes"] for p in st.session_state.proyectos]))
            # Ordenar meses cronológicamente usando el diccionario inverso
            meses_ordenados = sorted(meses_disponibles, key=lambda x: list(meses_es.values()).index(x))
            
            mes_seleccionado = st.selectbox("Selecciona el mes a exportar:", meses_ordenados)
            
            # Filtro lógico
            lista_a_exportar = [p for p in st.session_state.proyectos if p["Mes"] == mes_seleccionado]
            df_a_exportar = df_resultados[df_resultados["Mes"] == mes_seleccionado]
            
            titulo_doc = f"REPORTE INTERNO DE RENTABILIDAD - {mes_seleccionado.upper()}"
            nombre_archivo = f"Pro
