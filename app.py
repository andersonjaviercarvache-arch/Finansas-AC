import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import datetime
import json
import plotly.express as px

# =========================================================================
# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS (TEMA AZUL CORPORATIVO) ---
# =========================================================================
st.set_page_config(page_title="Gestor Financiero", layout="wide", page_icon="📊")

st.markdown("""
    <style>
    /* Dejamos que el fondo de la app respete el tema nativo (Claro/Oscuro) de Streamlit */
    
    /* Barra lateral azul corporativo */
    [data-testid="stSidebar"] {
        background-color: #1f3c88 !important;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    /* Tarjetas de Métricas (KPIs) adaptables al tema del usuario */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color); 
        border-radius: 6px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    
    /* Título principal adaptable */
    .titulo-dashboard {
        text-align: center;
        color: var(--text-color); 
        margin-bottom: 0;
    }
    
    /* Ocultar elementos por defecto de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Botones primarios en azul corporativo */
    button[kind="primary"] {
        background-color: #1f77b4 !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 5px !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background-color: #155a8a !important;
    }
    </style>
""", unsafe_allow_html=True)

# Título Limpio Inteligente
st.markdown("<h2 class='titulo-dashboard'>📊 Sistema de Ingeniería de Costos y Control Financiero</h2>", unsafe_allow_html=True)
st.write("---")

# --- CONFIGURACIÓN DE LA BASE DE DATOS LOCAL (JSON) ---
DB_FILE = "proyectos_db.json"

def cargar_base_de_datos():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def guardar_en_base_de_datos(proyectos):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(proyectos, f, ensure_ascii=False, indent=4)

if 'proyectos' not in st.session_state:
    st.session_state.proyectos = cargar_base_de_datos()

meses_lista = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# =========================================================================
# --- BARRA LATERAL (SIDEBAR) ---
# =========================================================================
with st.sidebar:
    st.markdown("## 👨‍💻 Menú de Usuario")
    st.write("---")
    
    total_proyectos = len(st.session_state.proyectos)
    
    if total_proyectos > 0:
        st.markdown(f"**Proyectos Registrados:** {total_proyectos}")
        df_side = pd.DataFrame([{k: v for k, v in p.items() if not k.startswith("_")} for p in st.session_state.proyectos])
        total_ganancia_side = df_side["Ganancia Neta"].sum() if not df_side.empty else 0.0
        
        st.markdown(f"**Utilidad Neta Actual:**")
        st.markdown(f"<h3 style='color:#4dd0e1 !important; margin-top:0;'>${total_ganancia_side:,.2f}</h3>", unsafe_allow_html=True)
    else:
        st.warning("Sistema en blanco.")
        
    st.write("---")
    st.caption("© 2026 | Sistema Interno")

# --- LÓGICA DE EXPORTACIÓN A PDF ---
def generar_pdf(lista_proyectos, df_interno, tipo_exportacion, titulo_reporte=None):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=10, top=15, right=10)
    pdf.add_page() 
    
    pdf.set_font("Helvetica", 'I', 8)
    pdf.cell(0, 4, f"Fecha de Emisión: {datetime.date.today().strftime('%d/%m/%Y')}", new_x="LMARGIN", new_y="NEXT", align='R')
    pdf.ln(2)

    if tipo_exportacion == "individual":
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 8, "COTIZACIÓN COMERCIAL", new_x="LMARGIN", new_y="NEXT", align='C')
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
        pdf.ln(8)

        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 8, "DESGLOSE DETALLADO DE COSTOS OPERATIVOS", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(5)

        for p in lista_proyectos:
            pdf.set_font("Helvetica", 'B', 10)
            fecha_str = p.get("Fecha", "N/A")
            pdf.cell(0, 8, f"Proyecto: {p['Proyecto']} (Fecha: {fecha_str} | Periodo: {p['Mes']} {p['Año']} | Duración: {p['_Dias']} días)", new_x="LMARGIN", new_y="NEXT", align='L')
            
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(0, 6, "Costo de Personal (Asignado a la obra):", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(70, 6, "Rol / Integrante", border=1)
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
            
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(0, 6, f"Desglose de Costos Operativos y Viáticos ({p.get('_Tipo_Ubicacion', 'Fuera de la ciudad')}):", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(60, 6, "Concepto", border=1)
            pdf.cell(40, 6, "Diario/Noche (c/u)", border=1, align='C')
            pdf.cell(30, 6, "Días", border=1, align='C')
            pdf.cell(60, 6, "Total Grupo / Rubro", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
            
            pdf.set_font("Helvetica", '', 9)
            num_personas = len(p["_Personal"])
            suma_viaticos = 0
            
            for concepto, datos in p["_Viaticos"].items():
                if datos.get("tipo", "por_persona") == "por_persona":
                    total_concepto = datos["costo"] * datos["dias"] * num_personas
                    pdf.cell(60, 6, concepto, border=1)
                    pdf.cell(40, 6, f"${datos['costo']:,.2f}", border=1, align='C')
                    pdf.cell(30, 6, str(datos['dias']), border=1, align='C')
                else: 
                    total_concepto = datos["costo"]
                    pdf.cell(60, 6, concepto, border=1)
                    pdf.cell(40, 6, "Fijo Individual", border=1, align='C')
                    pdf.cell(30, 6, "-", border=1, align='C')
                    
                suma_viaticos += total_concepto
                pdf.cell(60, 6, f"${total_concepto:,.2f}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
                
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(130, 6, "TOTAL COSTOS OPERATIVOS / VIÁTICOS", border=1, align='R')
            pdf.cell(60, 6, f"${suma_viaticos:,.2f}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(3)
            
            # Incorporación del campo Traslado de Equipos (Usando .get para compatibilidad con data antigua)
            pdf.set_font("Helvetica", '', 9)
            pdf.cell(0, 6, f"Materiales y Otros Costos: ${p.get('_Materiales', 0.0):,.2f}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 6, f"Traslado de Equipos: ${p.get('_Traslado', 0.0):,.2f}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(6)
            
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 8, "REPORTE INTERNO DE GANANCIAS Y PÉRDIDAS (P&L)", new_x="LMARGIN", new_y="NEXT", align='L')
            pdf.ln(2)
            
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(95, 6, "GANANCIAS / INGRESOS (Entradas)", border=1, align='C')
            pdf.cell(95, 6, "PÉRDIDAS / COSTOS (Salidas)", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
            
            pdf.set_font("Helvetica", '', 9)
            pdf.cell(55, 6, " Precio de Venta Cobrado:", border='LTB')
            pdf.cell(40, 6, f"${p['PRECIO VENTA FINAL']:,.2f} ", border='RTB', align='R')
            pdf.cell(55, 6, " Costos Directos:", border='LTB')
            pdf.cell(40, 6, f"${p['Costo Directo']:,.2f} ", border='RTB', align='R', new_x="LMARGIN", new_y="NEXT")
            
            pdf.cell(55, 6, "", border='LTB')
            pdf.cell(40, 6, "", border='RTB', align='R')
            pdf.cell(55, 6, " Fondo de Imprevistos:", border='LTB')
            pdf.cell(40, 6, f"${p['Fondo Imprevistos']:,.2f} ", border='RTB', align='R', new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(55, 6, " TOTAL INGRESOS PROYECTO:", border=1)
            pdf.cell(40, 6, f"${p['PRECIO VENTA FINAL']:,.2f} ", border=1, align='R')
            
            total_egresos_p = p['Costo Directo'] + p['Fondo Imprevistos']
            pdf.cell(55, 6, " TOTAL COSTOS OPERATIVOS:", border=1)
            pdf.cell(40, 6, f"${total_egresos_p:,.2f} ", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
            
            pdf.ln(2)
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(130, 8, " RESULTADO / BALANCE NETO:", border=1, align='R')
            pdf.cell(60, 8, f"${p['Ganancia Neta']:,.2f} ", border=1, align='R', new_x="LMARGIN", new_y="NEXT")

    elif tipo_exportacion == "todos":
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 8, titulo_reporte, new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(5)
        
        pdf.set_font("Helvetica", 'B', 8)
        pdf.cell(20, 8, "Fecha", border=1, align='C')
        pdf.cell(30, 8, "Proyecto", border=1, align='C')
        pdf.cell(23, 8, "Costo Dir.", border=1, align='C')
        pdf.cell(23, 8, "Imprev.", border=1, align='C')
        pdf.cell(23, 8, "Ganancia", border=1, align='C')
        pdf.cell(23, 8, "IVA (15%)", border=1, align='C')
        pdf.cell(24, 8, "Venta Final", border=1, align='C')
        pdf.cell(24, 8, "Precio Total", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.set_font("Helvetica", '', 8)
        sum_costo = sum_imprev = sum_ganancia = sum_iva = sum_venta = sum_total = 0
        
        for _, row in df_interno.iterrows():
            f_obra = str(row.get('Fecha', 'N/A'))
            if f_obra in ['0', '0.0', 'nan']: f_obra = 'N/A'
                
            nombre = str(row['Proyecto'])[:16]
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
            
            pdf.cell(20, 8, f_obra, border=1, align='C')
            pdf.cell(30, 8, nombre, border=1)
            pdf.cell(23, 8, f"${c_directo:,.2f}", border=1, align='R')
            pdf.cell(23, 8, f"${c_imprevisto:,.2f}", border=1, align='R')
            pdf.cell(23, 8, f"${c_ganancia:,.2f}", border=1, align='R')
            pdf.cell(23, 8, f"${iva:,.2f}", border=1, align='R')
            pdf.cell(24, 8, f"${p_venta:,.2f}", border=1, align='R')
            pdf.cell(24, 8, f"${p_total:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align='R')
            
        pdf.set_font("Helvetica", 'B', 8)
        pdf.cell(50, 8, "TOTALES ACUMULADOS", border=1, align='R')
        pdf.cell(23, 8, f"${sum_costo:,.2f}", border=1, align='R')
        pdf.cell(23, 8, f"${sum_imprev:,.2f}", border=1, align='R')
        pdf.cell(23, 8, f"${sum_ganancia:,.2f}", border=1, align='R')
        pdf.cell(23, 8, f"${sum_iva:,.2f}", border=1, align='R')
        pdf.cell(24, 8, f"${sum_venta:,.2f}", border=1, align='R')
        pdf.cell(24, 8, f"${sum_total:,.2f}", border=1, new_x="LMARGIN", new_y="NEXT", align='R')
        pdf.ln(6)

        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, "REPORTE CONSOLIDADO DE GANANCIAS Y PÉRDIDAS (P&L)", new_x="LMARGIN", new_y="NEXT", align='L')
        pdf.ln(2)
        
        pdf.set_font("Helvetica", 'B', 9)
        pdf.cell(95, 6, "GANANCIAS / INGRESOS ACUMULADOS", border=1, align='C')
        pdf.cell(95, 6, "PÉRDIDAS / COSTOS Y RESERVAS CONSOLIDADAS", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.set_font("Helvetica", '', 9)
        pdf.cell(55, 6, " Facturación Consolidada (Subtotal):", border='LTB')
        pdf.cell(40, 6, f"${sum_venta:,.2f} ", border='RTB', align='R')
        pdf.cell(55, 6, " Costos Directos Totales:", border='LTB')
        pdf.cell(40, 6, f"${sum_costo:,.2f} ", border='RTB', align='R', new_x="LMARGIN", new_y="NEXT")
        
        pdf.cell(55, 6, "", border='LTB')
        pdf.cell(40, 6, "", border='RTB', align='R')
        pdf.cell(55, 6, " Fondos de Imprevistos Totales:", border='LTB')
        pdf.cell(40, 6, f"${sum_imprev:,.2f} ", border='RTB', align='R', new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font("Helvetica", 'B', 9)
        pdf.cell(55, 6, " TOTAL INGRESOS GENERALES:", border=1)
        pdf.cell(40, 6, f"${sum_venta:,.2f} ", border=1, align='R')
        
        total_egresos_todos = sum_costo + sum_imprev
        pdf.cell(55, 6, " TOTAL INVERSIÓN LOGÍSTICA:", border=1)
        pdf.cell(40, 6, f"${total_egresos_todos:,.2f} ", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(2)
        pdf.set_font("Helvetica", 'B', 10)
        pdf.cell(130, 8, " RESULTADO / BALANCE NETO TOTAL:", border=1, align='R')
        pdf.cell(60, 8, f"${sum_ganancia:,.2f} ", border=1, align='R', new_x="LMARGIN", new_y="NEXT")

    temp_file = "temp_report.pdf"
    pdf.output(temp_file)
    with open(temp_file, "rb") as f:
        pdf_bytes = f.read()
    os.remove(temp_file)
    return pdf_bytes

# =========================================================================
# --- INTERFAZ PRINCIPAL CON PESTAÑAS MODERNAS ---
# =========================================================================

tab_dashboard, tab_registro, tab_reportes = st.tabs(["📊 Dashboard Analítico", "✍️ Cargar Operación", "📑 Informes y Exportación"])

# -------------------------------------------------------------------------
# PESTAÑA 1: DASHBOARD INTERACTIVO (PLOTLY SIN MODEBAR)
# -------------------------------------------------------------------------
with tab_dashboard:
    if st.session_state.proyectos:
        st.markdown("### Resumen Financiero General")
        
        df_global = pd.DataFrame([{k: v for k, v in p.items() if not k.startswith("_")} for p in st.session_state.proyectos]).fillna(0)
        df_global["Costo Operativo"] = df_global["Costo Directo"] + df_global["Fondo Imprevistos"]
        
        resumen_mensual = df_global.groupby("Mes")[["Costo Operativo", "Ganancia Neta", "IVA (15%)", "PRECIO TOTAL", "PRECIO VENTA FINAL"]].sum().reset_index()
        resumen_mensual["Mes_Num"] = resumen_mensual["Mes"].apply(lambda x: meses_lista.index(x) if x in meses_lista else 99)
        resumen_mensual = resumen_mensual.sort_values("Mes_Num").drop("Mes_Num", axis=1)
        
        t_costo = resumen_mensual["Costo Operativo"].sum()
        t_ganancia = resumen_mensual["Ganancia Neta"].sum()
        t_iva = resumen_mensual["IVA (15%)"].sum()
        t_facturado = resumen_mensual["PRECIO TOTAL"].sum()
        
        col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)
        col_kpi1.metric("Facturación Total", f"${t_facturado:,.2f}")
        col_kpi2.metric("Inversión / Costos", f"${t_costo:,.2f}")
        col_kpi3.metric("Utilidad Neta", f"${t_ganancia:,.2f}")
        col_kpi4.metric("IVA Acumulado", f"${t_iva:,.2f}")
        
        st.write("---")
        
        col_graf1, col_graf2 = st.columns([2, 1])
        
        with col_graf1:
            st.markdown("#### Ingresos vs Egresos (Mensual)")
            
            df_bar = resumen_mensual.melt(id_vars=["Mes"], value_vars=["PRECIO VENTA FINAL", "Costo Operativo"], 
                                          var_name="Indicador", value_name="Monto")
            df_bar["Indicador"] = df_bar["Indicador"].replace({"PRECIO VENTA FINAL": "Ingresos", "Costo Operativo": "Costos"})
            
            fig_bar = px.bar(df_bar, x="Mes", y="Monto", color="Indicador", barmode="group",
                             color_discrete_map={"Ingresos": "#1f77b4", "Costos": "#aec7e8"},
                             text_auto='.2s')
            
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                xaxis_title="", yaxis_title="",
                legend_title="", hovermode="x unified", margin=dict(l=0, r=0, t=20, b=0)
            )
            st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

        with col_graf2:
            st.markdown("#### Distribución de Costos y Ganancias")
            df_pie = pd.DataFrame({
                "Categoría": ["Costo Operativo", "IVA Retenido", "Utilidad Neta"],
                "Monto": [t_costo, t_iva, t_ganancia]
            })
            
            fig_donut = px.pie(df_pie, values='Monto', names='Categoría', hole=0.6,
                               color='Categoría',
                               color_discrete_map={"Costo Operativo": "#aec7e8", "IVA Retenido": "#ff7f0e", "Utilidad Neta": "#1f77b4"})
            
            fig_donut.update_layout(margin=dict(l=0, r=0, t=20, b=0), showlegend=True, 
                                    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5))
            st.plotly_chart(fig_donut, use_container_width=True, config={'displayModeBar': False})

    else:
        st.info("Aún no hay datos suficientes para generar los gráficos. Registra un proyecto primero.")

# -------------------------------------------------------------------------
# PESTAÑA 2: REGISTRAR PROYECTO
# -------------------------------------------------------------------------
with tab_registro:
    st.markdown("### 📝 Cargar Nueva Operación")
    
    with st.container():
        col_info, col_dias, col_mes, col_anio, col_fecha = st.columns([2, 1, 1, 1, 1])
        nombre_proyecto = col_info.text_input("Nombre / Referencia", placeholder="Ej: Proyecto Norte")
        dias_trabajo = col_dias.number_input("Días Previstos", min_value=1, value=4)
        
        mes_actual_idx = datetime.date.today().month - 1
        mes_proyecto = col_mes.selectbox("Mes Contable", meses_lista, index=mes_actual_idx)
        anio_proyecto = col_anio.number_input("Año", min_value=2020, value=datetime.date.today().year)
        fecha_obra = col_fecha.date_input("Fecha Exacta", value=datetime.date.today())

    st.write("") 

    with st.expander("👥 Configuración de Mano de Obra (Hasta 10)", expanded=False):
        df_personal_base = pd.DataFrame([
            {"Rol": "Supervisor", "Costo Día ($)": 50.00, "Asignado": True},
            {"Rol": "Técnico 1", "Costo Día ($)": 37.50, "Asignado": True},
            {"Rol": "Técnico 2", "Costo Día ($)": 37.50, "Asignado": True},
            {"Rol": "Técnico 3", "Costo Día ($)": 37.50, "Asignado": False},
            {"Rol": "Técnico 4", "Costo Día ($)": 37.50, "Asignado": False},
            {"Rol": "Técnico 5", "Costo Día ($)": 37.50, "Asignado": False},
            {"Rol": "Técnico 6", "Costo Día ($)": 37.50, "Asignado": False},
            {"Rol": "Técnico 7", "Costo Día ($)": 37.50, "Asignado": False},
            {"Rol": "Técnico 8", "Costo Día ($)": 37.50, "Asignado": False},
            {"Rol": "Ayudante", "Costo Día ($)": 25.00, "Asignado": False}
        ])
        df_personal_editado = st.data_editor(df_personal_base, use_container_width=True, hide_index=True)

    with st.expander("🚗 Viáticos y Logística", expanded=False):
        tipo_ubicacion = st.selectbox("Ubicación", ["Fuera de la ciudad", "Dentro de la ciudad"])
        
        costo_viaticos_total = 0.0
        dict_viaticos_guardar = {}
        
        if tipo_ubicacion == "Fuera de la ciudad":
            st.markdown("##### 🛣️ Parámetros Foráneos (Por Persona)")
            col_v1, col_v2, col_v3, col_v4 = st.columns(4)
            with col_v1:
                alim_costo = st.number_input("Alimentación/Día ($)", min_value=0.0, value=15.0, key="alim_c_out")
                alim_dias = st.number_input("Días Alimentación", min_value=0, value=dias_trabajo, key="alim_d_out")
            with col_v2:
                mov_costo = st.number_input("Pasajes/Día ($)", min_value=0.0, value=15.0, key="mov_c_out")
                mov_dias = st.number_input("Días Movilización", min_value=0, value=dias_trabajo, key="mov_d_out")
            with col_v3:
                hidra_costo = st.number_input("Hidratación/Día ($)", min_value=0.0, value=10.0, key="hidra_c_out")
                hidra_dias = st.number_input("Días Hidratación", min_value=0, value=dias_trabajo, key="hidra_d_out")
            with col_v4:
                hosp_costo = st.number_input("Hospedaje/Noche ($)", min_value=0.0, value=20.0, key="hosp_c_out")
                hosp_dias = st.number_input("Noches Hotel", min_value=0, value=max(0, dias_trabajo - 1), key="hosp_d_out")

            st.markdown("##### 🔧 Costos Fijos Adicionales (Global)")
            visita_tecnica_out = st.number_input("Visita Técnica / Configuración ($)", min_value=0.0, value=30.0, key="vis_tec_out")

            personal_activo = df_personal_editado[df_personal_editado["Asignado"] == True]
            num_personas = len(personal_activo)
            
            viatico_total_pp = (alim_costo * alim_dias) + (mov_costo * mov_dias) + (hidra_costo * hidra_dias) + (hosp_costo * hosp_dias)
            costo_viaticos_total = (viatico_total_pp * num_personas) + visita_tecnica_out
            
            dict_viaticos_guardar = {
                "Alimentación": {"costo": alim_costo, "dias": alim_dias, "tipo": "por_persona"},
                "Movilización": {"costo": mov_costo, "dias": mov_dias, "tipo": "por_persona"},
                "Hidratación": {"costo": hidra_costo, "dias": hidra_dias, "tipo": "por_persona"},
                "Hospedaje": {"costo": hosp_costo, "dias": hosp_dias, "tipo": "por_persona"},
                "Visita Técnica (Global)": {"costo": visita_tecnica_out, "dias": 1, "tipo": "individual"}
            }
        else: 
            st.markdown("##### 🏙️ Parámetros Locales (Variables Mixtas)")
            col_dentro1, col_dentro2, col_dentro3 = st.columns(3)
            with col_dentro1:
                alim_costo_in = st.number_input("Alimentación Grupal/Día", min_value=0.0, value=15.0, key="alim_c_in")
                alim_dias_in = st.number_input("Días aplicables", min_value=0, value=dias_trabajo, key="alim_d_in")
            with col_dentro2:
                mov_total_in = st.number_input("Movilización Fija (Global)", min_value=0.0, value=25.0, key="mov_total_in")
            with col_dentro3:
                visita_config_in = st.number_input("Visita Técnica (Global)", min_value=0.0, value=30.0, key="vis_config_in")

            personal_activo = df_personal_editado[df_personal_editado["Asignado"] == True]
            num_personas = len(personal_activo)
            
            total_alimentacion_in = alim_costo_in * alim_dias_in * num_personas
            costo_viaticos_total = total_alimentacion_in + mov_total_in + visita_config_in
            
            dict_viaticos_guardar = {
                "Alimentación": {"costo": alim_costo_in, "dias": alim_dias_in, "tipo": "por_persona"},
                "Movilización (Individual)": {"costo": mov_total_in, "dias": 1, "tipo": "individual"},
                "Visita de Configuración (Individual)": {"costo": visita_config_in, "dias": 1, "tipo": "individual"}
            }

    st.markdown("### 🛠️ Materiales, Equipos y Logística Extra")
    
    col_mat1, col_mat2 = st.columns(2)
    with col_mat1:
        costo_materiales = st.number_input("Costo Bruto Suministros / Subcontratos ($)", min_value=0.0, value=0.0, step=50.0)
    with col_mat2:
        costo_traslado = st.number_input("Traslado de Equipos ($)", min_value=0.0, value=0.0, step=50.0)

    st.write("---")
    st.markdown("### 📈 Simulación y Precios")
    
    col_pct1, col_pct2 = st.columns(2)
    pct_imprevistos = col_pct1.slider("Imprevistos (%)", min_value=0, max_value=100, value=20, step=5)
    pct_ganancia_sugerida = col_pct2.slider("Margen de Utilidad (%)", min_value=0, max_value=100, value=40, step=5)

    costo_mano_obra = personal_activo["Costo Día ($)"].sum() * dias_trabajo
    costo_directo = costo_mano_obra + costo_viaticos_total + costo_materiales + costo_traslado
    
    reserva_imprevistos = costo_directo * (pct_imprevistos / 100)
    ganancia_calculada = costo_directo * (pct_ganancia_sugerida / 100)
    precio_sugerido = costo_directo + reserva_imprevistos + ganancia_calculada

    precio_venta_final = st.number_input(
        f"Ajuste Precio a Facturar (Sugerido: ${precio_sugerido:,.2f})", 
        min_value=0.0, 
        value=float(precio_sugerido), 
        step=10.0
    )

    ganancia_real = precio_venta_final - costo_directo - reserva_imprevistos
    iva_monto = precio_venta_final * 0.15
    precio_total_con_iva = precio_venta_final + iva_monto

    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("Costo Ejecutado", f"${costo_directo:,.2f}")
    col_s2.metric("Fondo Contingencia", f"${reserva_imprevistos:,.2f}")
    col_s3.metric("Utilidad Neta", f"${ganancia_real:,.2f}")
    col_s4.metric("Facturación Base", f"${precio_venta_final:,.2f}")
    
    st.write("")
    
    c_btn1, c_btn2, c_btn3 = st.columns([1,2,1])
    with c_btn2:
        if st.button("💾 REGISTRAR OPERACIÓN", type="primary", use_container_width=True):
            if nombre_proyecto:
                nombres_existentes = [p["Proyecto"] for p in st.session_state.proyectos]
                if nombre_proyecto in nombres_existentes:
                    st.error("Error: Obra ya registrada. Usa un ID único.")
                else:
                    st.session_state.proyectos.append({
                        "Año": anio_proyecto,
                        "Mes": mes_proyecto,
                        "Fecha": fecha_obra.strftime("%d/%m/%Y"), 
                        "Proyecto": nombre_proyecto,
                        "Costo Directo": costo_directo,
                        "Fondo Imprevistos": reserva_imprevistos, 
                        "Ganancia Neta": ganancia_real,           
                        "PRECIO VENTA FINAL": precio_venta_final,
                        "IVA (15%)": iva_monto,
                        "PRECIO TOTAL": precio_total_con_iva,
                        "_Dias": dias_trabajo,
                        "_Personal": personal_activo.to_dict('records'),
                        "_Tipo_Ubicacion": tipo_ubicacion,
                        "_Viaticos": dict_viaticos_guardar,
                        "_Materiales": costo_materiales,
                        "_Traslado": costo_traslado
                    })
                    guardar_en_base_de_datos(st.session_state.proyectos)
                    st.success("✅ Guardado Exitosamente.")
                    st.rerun()
            else:
                st.error("⚠️ Nombre requerido.")

# -------------------------------------------------------------------------
# PESTAÑA 3: INFORMES Y EXTRACCIÓN
# -------------------------------------------------------------------------
with tab_reportes:
    if st.session_state.proyectos:
        datos_publicos = [{k: v for k, v in p.items() if not k.startswith("_")} for p in st.session_state.proyectos]
        df_resultados = pd.DataFrame(datos_publicos).fillna(0)
        
        columnas_ordenadas = ["Año", "Mes", "Fecha", "Proyecto", "Costo Directo", "Fondo Imprevistos", "Ganancia Neta", "PRECIO VENTA FINAL", "IVA (15%)", "PRECIO TOTAL"]
        df_resultados = df_resultados[[col for col in columnas_ordenadas if col in df_resultados.columns]]
        formato_moneda = {col: "${:,.2f}" for col in df_resultados.columns if col not in ["Mes", "Proyecto", "Año", "Fecha"]}

        st.markdown("### Informes de Facturación y Actividad")
        
        tipo_reporte = st.radio(
            "Filtro de Exportación:",
            ["Mes Específico", "Histórico Anual", "Documento de Proyecto"],
            horizontal=True
        )
        st.write("---")

        col_rep1, col_rep2 = st.columns([1, 2])

        if tipo_reporte == "Mes Específico":
            with col_rep1:
                meses_disponibles = list(set([p["Mes"] for p in st.session_state.proyectos]))
                meses_ordenados = sorted(meses_disponibles, key=lambda x: meses_lista.index(x))
                mes_seleccionado = st.selectbox("Selecciona Mes:", meses_ordenados)
                
            with col_rep2:
                lista_a_exportar = [p for p in st.session_state.proyectos if p["Mes"] == mes_seleccionado]
                df_a_exportar = df_resultados[df_resultados["Mes"] == mes_seleccionado]
                st.dataframe(df_a_exportar.style.format(formato_moneda), use_container_width=True, hide_index=True)
                
                titulo_doc = f"REPORTE INTERNO DE CONTABILIDAD - {mes_seleccionado.upper()}"
                nombre_archivo = f"Balance_{mes_seleccionado}.pdf"
                pdf_mes = generar_pdf(lista_a_exportar, df_a_exportar, tipo_exportacion="todos", titulo_reporte=titulo_doc)
                st.download_button(label="📥 Descargar PDF", data=pdf_mes, file_name=nombre_archivo, mime="application/pdf", type="primary")

        elif tipo_reporte == "Histórico Anual":
            st.dataframe(df_resultados.style.format(formato_moneda), use_container_width=True, hide_index=True)
            titulo_doc = "REPORTE INTERNO DE CONTABILIDAD ENERO A DICIEMBRE"
            pdf_anual = generar_pdf(st.session_state.proyectos, df_resultados, tipo_exportacion="todos", titulo_reporte=titulo_doc)
            st.download_button(label="📥 Descargar Histórico PDF", data=pdf_anual, file_name="Historico.pdf", mime="application/pdf", type="primary")
            
        elif tipo_reporte == "Documento de Proyecto":
            with col_rep1:
                nombres_proyectos = [p["Proyecto"] for p in st.session_state.proyectos]
                proyecto_seleccionado = st.selectbox("Selecciona Obra:", nombres_proyectos)
            
            with col_rep2:
                lista_a_exportar = [p for p in st.session_state.proyectos if p["Proyecto"] == proyecto_seleccionado]
                df_a_exportar = df_resultados[df_resultados["Proyecto"] == proyecto_seleccionado]
                st.dataframe(df_a_exportar.style.format(formato_moneda), use_container_width=True, hide_index=True)
                
                nombre_archivo = f"Cotizacion_{proyecto_seleccionado.replace(' ', '_')}.pdf"
                pdf_individual = generar_pdf(lista_a_exportar, df_a_exportar, tipo_exportacion="individual")
                st.download_button(label="📄 Descargar Formato PDF", data=pdf_individual, file_name=nombre_archivo, mime="application/pdf", type="primary")

        st.write("---")
        with st.expander("⚙️ Gestión y Depuración de Registros"):
            nombres_proyectos_del = [p["Proyecto"] for p in st.session_state.proyectos]
            proyecto_a_eliminar = st.selectbox("Selecciona para borrar:", nombres_proyectos_del, key="del_proj_box")
            if st.button("🗑️ Eliminar Definitivamente"):
                st.session_state.proyectos = [p for p in st.session_state.proyectos if p["Proyecto"] != proyecto_a_eliminar]
                guardar_en_base_de_datos(st.session_state.proyectos)
                st.warning("Eliminado.")
                st.rerun()
    else:
        st.info("⚠️ Sin datos.")
