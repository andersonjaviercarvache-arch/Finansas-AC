import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

st.set_page_config(page_title="Gestor de Rentabilidad", layout="wide")

st.title("📊 Gestor Financiero - Latitud Solar")

# --- INICIALIZAR MEMORIA ---
if 'proyectos' not in st.session_state:
    st.session_state.proyectos = []

# --- SECCIÓN: REGISTRO DE PROYECTO ---
st.header("Registrar Nuevo Proyecto")

col_info, col_dias = st.columns(2)
nombre_proyecto = col_info.text_input("Nombre del Proyecto")
dias_trabajo = col_dias.number_input("Días de Trabajo en Obra (Personal)", min_value=1, value=4)

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

# --- NUEVA SECCIÓN DE VIÁTICOS INDEPENDIENTES ---
st.subheader("2. Desglose de Viáticos (Por Persona)")
st.write("Ingresa el valor diario y cuántos días aplica cada rubro (por defecto toma los días de la obra).")

col_v1, col_v2, col_v3 = st.columns(3)

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

# Cálculo individual por rubro
total_alim_pp = alim_costo * alim_dias
total_mov_pp = mov_costo * mov_dias
total_hidra_pp = hidra_costo * hidra_dias

viatico_total_pp = total_alim_pp + total_mov_pp + total_hidra_pp
st.info(f"**Total acumulado de viáticos por cada persona (durante toda la obra):** ${viatico_total_pp:.2f}")

st.write("---")

st.subheader("3. Materiales y Otros")
costo_materiales = st.number_input("Costo de Materiales o Equipos ($)", min_value=0.0, value=0.0, step=50.0)

st.write("---")

# --- CÁLCULO DE MÁRGENES Y PRECIO FINAL ---
st.subheader("4. Ajuste de Márgenes y Precio de Venta")

col_pct1, col_pct2 = st.columns(2)
pct_imprevistos = col_pct1.slider("Porcentaje para Imprevistos (%)", min_value=0, max_value=100, value=20, step=5)
pct_ganancia = col_pct2.slider("Porcentaje de Ganancia (%)", min_value=0, max_value=100, value=40, step=5)

personal_activo = df_personal_editado[df_personal_editado["Asignado"] == True]
num_personas = len(personal_activo)

# Nómina = días generales de la obra. Viáticos = usan sus propios días multiplicados por la cantidad de personas.
costo_mano_obra = personal_activo["Costo Día ($)"].sum() * dias_trabajo
costo_viaticos_total = viatico_total_pp * num_personas
costo_directo = costo_mano_obra + costo_viaticos_total + costo_materiales

reserva_imprevistos = costo_directo * (pct_imprevistos / 100)
ganancia_esperada = costo_directo * (pct_ganancia / 100)

precio_venta_final = costo_directo + reserva_imprevistos + ganancia_esperada
iva_monto = precio_venta_final * 0.15
precio_total_con_iva = precio_venta_final + iva_monto

col_s1, col_s2, col_s3, col_s4 = st.columns(4)
col_s1.metric("Costo Directo", f"${costo_directo:,.2f}")
col_s2.metric(f"Imprevistos ({pct_imprevistos}%)", f"${reserva_imprevistos:,.2f}")
col_s3.metric(f"Ganancia ({pct_ganancia}%)", f"${ganancia_esperada:,.2f}")
col_s4.metric("PRECIO DE VENTA FINAL", f"${precio_venta_final:,.2f}")

st.success(f"**PRECIO DE VENTA FINAL:** ${precio_venta_final:,.2f}  |  **IVA (15%):** ${iva_monto:,.2f}  |  **PRECIO TOTAL:** ${precio_total_con_iva:,.2f}")

if st.button("Guardar Proyecto en el Mes", type="primary"):
    if nombre_proyecto:
        # Guardar todo el detalle para el PDF, ahora incluyendo los días específicos de los viáticos
        st.session_state.proyectos.append({
            "Proyecto": nombre_proyecto,
            "Costo Directo": costo_directo,
            f"Imprevistos ({pct_imprevistos}%)": reserva_imprevistos,
            f"Ganancia ({pct_ganancia}%)": ganancia_esperada,
            "PRECIO VENTA FINAL": precio_venta_final,
            "IVA (15%)": iva_monto,
            "PRECIO TOTAL": precio_total_con_iva,
            "_Dias": dias_trabajo,
            "_Personal": personal_activo.to_dict('records'),
            "_Viaticos": {
                "Alimentación": {"costo": alim_costo, "dias": alim_dias},
                "Movilización": {"costo": mov_costo, "dias": mov_dias},
                "Hidratación": {"costo": hidra_costo, "dias": hidra_dias}
            },
            "_Materiales": costo_materiales
        })
        st.success(f"Proyecto '{nombre_proyecto}' registrado exitosamente.")
    else:
        st.error("Por favor, ingresa el nombre del proyecto en la parte superior.")

# --- SECCIÓN: REPORTE MENSUAL Y DESCARGAS ---
st.write("---")
st.header("Reporte Mensual y Cotizaciones")

if st.session_state.proyectos:
    # Crear DataFrame solo con las columnas públicas
    datos_publicos = [{k: v for k, v in p.items() if not k.startswith("_")} for p in st.session_state.proyectos]
    df_resultados = pd.DataFrame(datos_publicos)
    
    # Formato visual en pantalla
    formato_moneda = {col: "${:,.2f}" for col in df_resultados.columns if col != "Proyecto"}
    df_mostrar = df_resultados.style.format(formato_moneda)
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    
    # --- LÓGICA DE EXPORTACIÓN A PDF ---
    def generar_pdf(lista_proyectos, df_interno):
        pdf = FPDF()
        
        # --- PÁGINA 1: COTIZACIÓN CLIENTE ---
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, "COTIZACIÓN COMERCIAL - LATITUD SOLAR", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(10)
        
        pdf.set_font("Helvetica", 'B', 11)
        pdf.cell(90, 10, "Descripción del Proyecto", border=1, align='C')
        pdf.cell(35, 10, "Subtotal", border=1, align='C')
        pdf.cell(30, 10, "IVA (15%)", border=1, align='C')
        pdf.cell(35, 10, "Total a Pagar", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.set_font("Helvetica", '', 10)
        for _, row in df_interno.iterrows():
            nombre = str(row['Proyecto'])[:45]
            pdf.cell(90, 10, nombre, border=1)
            pdf.cell(35, 10, f"${row['PRECIO VENTA FINAL']:,.2f}", border=1, align='R')
            pdf.cell(30, 10, f"${row['IVA (15%)']:,.2f}", border=1, align='R')
            pdf.cell(35, 10, f"${row['PRECIO TOTAL']:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align='R')
            
        pdf.ln(20)
        pdf.set_font("Helvetica", 'I', 10)
        pdf.cell(0, 10, "Nota: Los valores incluyen mano de obra, viáticos y equipos acordados.", new_x="LMARGIN", new_y="NEXT", align='C')
        
        # --- PÁGINA 2: REPORTE INTERNO ---
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, "REPORTE INTERNO DE RENTABILIDAD", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(10)
        
        col_imprevisto = [c for c in df_interno.columns if "Imprevistos" in c][0]
        col_ganancia = [c for c in df_interno.columns if "Ganancia" in c][0]
        
        pdf.set_font("Helvetica", 'B', 9)
        pdf.cell(60, 10, "Proyecto", border=1, align='C')
        pdf.cell(30, 10, "Costo Directo", border=1, align='C')
        pdf.cell(35, 10, "Fondo Imprevistos", border=1, align='C')
        pdf.cell(30, 10, "Ganancia Neta", border=1, align='C')
        pdf.cell(35, 10, "Precio de Venta", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.set_font("Helvetica", '', 9)
        for _, row in df_interno.iterrows():
            nombre = str(row['Proyecto'])[:30]
            pdf.cell(60, 10, nombre, border=1)
            pdf.cell(30, 10, f"${row['Costo Directo']:,.2f}", border=1, align='R')
            pdf.cell(35, 10, f"${row[col_imprevisto]:,.2f}", border=1, align='R')
            pdf.cell(30, 10, f"${row[col_ganancia]:,.2f}", border=1, align='R')
            pdf.cell(35, 10, f"${row['PRECIO VENTA FINAL']:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align='R')

        # --- PÁGINA 3+: ANEXO DETALLADO ---
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 10, "ANEXO: DESGLOSE DETALLADO DE COSTOS OPERATIVOS", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(10)

        for p in lista_proyectos:
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 10, f"Proyecto: {p['Proyecto']} (Duración Obra: {p['_Dias']} días)", new_x="LMARGIN", new_y="NEXT", align='L')
            
            # Tabla 1: Personal
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(0, 8, "Costo de Personal (Asignado a la obra):", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(60, 8, "Rol", border=1)
            pdf.cell(40, 8, "Costo Diario por Persona", border=1)
            pdf.cell(50, 8, "Total Rol (Todos los días)", border=1, new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", '', 9)
            for persona in p["_Personal"]:
                total_rol = persona["Costo Día ($)"] * p["_Dias"]
                pdf.cell(60, 8, str(persona["Rol"]), border=1)
                pdf.cell(40, 8, f"${persona['Costo Día ($)']:,.2f}", border=1, align='C')
                pdf.cell(50, 8, f"${total_rol:,.2f}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
            
            pdf.ln(5)
            
            # Tabla 2: Viáticos (Actualizada con los días específicos)
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(0, 8, "Desglose de Viáticos (Calculado para todo el personal asignado):", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(45, 8, "Concepto", border=1)
            pdf.cell(35, 8, "Diario (c/u)", border=1, align='C')
            pdf.cell(20, 8, "Días", border=1, align='C')
            pdf.cell(50, 8, "Costo Total del Grupo", border=1, new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", '', 9)
            num_personas = len(p["_Personal"])
            for concepto, datos in p["_Viaticos"].items():
                total_concepto = datos["costo"] * datos["dias"] * num_personas
                pdf.cell(45, 8, concepto, border=1)
                pdf.cell(35, 8, f"${datos['costo']:,.2f}", border=1, align='C')
                pdf.cell(20, 8, str(datos['dias']), border=1, align='C')
                pdf.cell(50, 8, f"${total_concepto:,.2f}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
            
            pdf.ln(5)
            # Otros
            pdf.set_font("Helvetica", '', 10)
            pdf.cell(0, 8, f"Materiales y Otros Costos: ${p['_Materiales']:,.2f}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
        # Generar y retornar PDF
        temp_file = "cotizacion_latitud_solar.pdf"
        pdf.output(temp_file)
        
        with open(temp_file, "rb") as f:
            pdf_bytes = f.read()
        os.remove(temp_file)
        return pdf_bytes

    # Procesar descarga
    pdf_generado = generar_pdf(st.session_state.proyectos, df_resultados)

    st.write("Genera tu archivo PDF. Incluye la cotización, tu reporte de márgenes y un anexo con el desglose exacto de pagos a técnicos y viáticos.")
    st.download_button(
        label="📥 Descargar Formato Completo (PDF)",
        data=pdf_generado,
        file_name="Cotizaciones_Latitud_Solar.pdf",
        mime="application/pdf",
        type="primary"
    )

else:
    st.info("Aún no tienes proyectos guardados. Configura uno en la parte superior y presiona 'Guardar Proyecto'.")
