import streamlit as st
import pandas as pd
from fpdf import FPDF
import os
import datetime
import json

# =========================================================================
# --- CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS AVANZADOS ---
# =========================================================================
st.set_page_config(page_title="Latitud Solar | Gestor Financiero", layout="wide", page_icon="☀️")

# Inyección de CSS para embellecer la interfaz (Modo Dashboard Profesional)
st.markdown("""
    <style>
    /* Fondo general más limpio */
    .stApp {
        background-color: #f4f7f6;
    }
    /* Banner del Título Principal */
    .main-header {
        background: linear-gradient(135deg, #004b87 0%, #0073e6 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
    }
    .main-header p {
        margin: 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    /* Tarjetas para las Métricas (st.metric) */
    div[data-testid="stMetric"] {
        background-color: white;
        border-radius: 10px;
        padding: 15px 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #ffb703; /* Color amarillo solar */
        transition: transform 0.2s ease-in-out;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
    }
    /* Ajustes a pestañas */
    button[data-baseweb="tab"] {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    /* Estilizar botones primarios */
    button[kind="primary"] {
        background-color: #ffb703 !important;
        color: #002b4d !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        transition: all 0.3s;
    }
    button[kind="primary"]:hover {
        background-color: #ff9800 !important;
        box-shadow: 0 4px 12px rgba(255, 152, 0, 0.4) !important;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado HTML personalizado
st.markdown("""
    <div class="main-header">
        <h1>☀️ LATITUD SOLAR</h1>
        <p>Sistema Inteligente de Ingeniería de Costos y Control Financiero</p>
    </div>
""", unsafe_allow_html=True)


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
# --- BARRA LATERAL DE RESUMEN (SIDEBAR) ---
# =========================================================================
with st.sidebar:
    st.markdown("### 👨‍💻 Panel de Usuario")
    st.write("Bienvenido al gestor operativo.")
    st.write("---")
    st.markdown("### 📊 Estado de la Base de Datos")
    
    total_proyectos = len(st.session_state.proyectos)
    
    if total_proyectos > 0:
        st.success(f"**{total_proyectos}** Proyectos Registrados")
        
        # Calcular un mini resumen rápido para la barra lateral
        df_side = pd.DataFrame([{k: v for k, v in p.items() if not k.startswith("_")} for p in st.session_state.proyectos])
        total_ganancia_side = df_side["Ganancia Neta"].sum() if not df_side.empty else 0.0
        
        st.info(f"💰 **Utilidad Neta Total:**\n${total_ganancia_side:,.2f}")
    else:
        st.warning("No hay proyectos registrados aún.")
        
    st.write("---")
    st.caption("Latitud Solar © 2026 | Sistema Interno")

# --- LÓGICA DE EXPORTACIÓN A PDF (INTACTA) ---
def generar_pdf(lista_proyectos, df_interno, tipo_exportacion, titulo_reporte=None):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(left=10, top=15, right=10)
    pdf.add_page() 
    
    pdf.set_font("Helvetica", 'I', 8)
    pdf.cell(0, 4, f"Fecha de Emisión del Reporte: {datetime.date.today().strftime('%d/%m/%Y')}", new_x="LMARGIN", new_y="NEXT", align='R')
    pdf.ln(2)

    if tipo_exportacion == "individual":
        # FORMATO INDIVIDUAL
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
        pdf.ln(8)

        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 8, "DESGLOSE DETALLADO DE COSTOS OPERATIVOS", new_x="LMARGIN", new_y="NEXT", align='C')
        pdf.ln(5)

        for p in lista_proyectos:
            pdf.set_font("Helvetica", 'B', 10)
            fecha_str = p.get("Fecha", "N/A")
            pdf.cell(0, 8, f"Proyecto: {p['Proyecto']} (Fecha de Ejecución: {fecha_str} | Periodo: {p['Mes']} {p['Año']} | Duración: {p['_Dias']} días)", new_x="LMARGIN", new_y="NEXT", align='L')
            
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
            
            pdf.set_font("Helvetica", '', 9)
            pdf.cell(0, 6, f"Materiales y Otros Costos: ${p['_Materiales']:,.2f}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(6)
            
            # REPORTE DE GANANCIAS Y PÉRDIDAS (INDIVIDUAL)
            pdf.set_font("Helvetica", 'B', 12)
            pdf.cell(0, 8, "REPORTE INTERNO DE GANANCIAS Y PÉRDIDAS (P&L)", new_x="LMARGIN", new_y="NEXT", align='L')
            pdf.ln(2)
            
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(95, 6, "GANANCIAS / INGRESOS (Entradas)", border=1, align='C')
            pdf.cell(95, 6, "PÉRDIDAS / COSTOS (Salidas e Inversión)", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
            
            pdf.set_font("Helvetica", '', 9)
            pdf.cell(55, 6, " Precio de Venta Cobrado:", border='LTB')
            pdf.cell(40, 6, f"${p['PRECIO VENTA FINAL']:,.2f} ", border='RTB', align='R')
            pdf.cell(55, 6, " Inversión de Costos Directos:", border='LTB')
            pdf.cell(40, 6, f"${p['Costo Directo']:,.2f} ", border='RTB', align='R', new_x="LMARGIN", new_y="NEXT")
            
            pdf.cell(55, 6, "", border='LTB')
            pdf.cell(40, 6, "", border='RTB', align='R')
            pdf.cell(55, 6, " Fondo de Imprevistos Asignado:", border='LTB')
            pdf.cell(40, 6, f"${p['Fondo Imprevistos']:,.2f} ", border='RTB', align='R', new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(55, 6, " TOTAL INGRESOS PROYECTO:", border=1)
            pdf.cell(40, 6, f"${p['PRECIO VENTA FINAL']:,.2f} ", border=1, align='R')
            
            total_egresos_p = p['Costo Directo'] + p['Fondo Imprevistos']
            pdf.cell(55, 6, " TOTAL COSTOS OPERATIVOS:", border=1)
            pdf.cell(40, 6, f"${total_egresos_p:,.2f} ", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
            
            pdf.ln(2)
            pdf.set_font("Helvetica", 'B', 10)
            pdf.cell(130, 8, " BALANCE NETO / UTILIDAD REAL DEL PROYECTO:", border=1, align='R')
            pdf.cell(60, 8, f"${p['Ganancia Neta']:,.2f} ", border=1, align='R', new_x="LMARGIN", new_y="NEXT")

    elif tipo_exportacion == "todos":
        # FORMATO CONSOLIDADO (Mensual/Anual)
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
            if f_obra in ['0', '0.0', 'nan']:
                f_obra = 'N/A'
                
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

        # REPORTE DE GANANCIAS Y PÉRDIDAS (CONSOLIDADO)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 8, "REPORTE CONSOLIDADO DE GANANCIAS Y PÉRDIDAS (P&L)", new_x="LMARGIN", new_y="NEXT", align='L')
        pdf.ln(2)
        
        pdf.set_font("Helvetica", 'B', 9)
        pdf.cell(95, 6, "GANANCIAS / INGRESOS ACUMULADOS", border=1, align='C')
        pdf.cell(95, 6, "PÉRDIDAS / COSTOS Y RESERVAS CONSOLIDADAS", border=1, new_x="LMARGIN", new_y="NEXT", align='C')
        
        pdf.set_font("Helvetica", '', 9)
        pdf.cell(55, 6, " Facturación Consolidada (Subtotal):", border='LTB')
        pdf.cell(40, 6, f"${sum_venta:,.2f} ", border='RTB', align='R')
        pdf.cell(55, 6, " Costos Directos Totales Ejecutados:", border='LTB')
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
        pdf.cell(130, 8, " BALANCE NETO / UTILIDAD OPERATIVA TOTAL:", border=1, align='R')
        pdf.cell(60, 8, f"${sum_ganancia:,.2f} ", border=1, align='R', new_x="LMARGIN", new_y="NEXT")

    temp_file = "temp_report.pdf"
    pdf.output(temp_file)
    with open(temp_file, "rb") as f:
        pdf_bytes = f.read()
    os.remove(temp_file)
    return pdf_bytes


# =========================================================================
# --- CREACIÓN DE LA INTERFAZ CON PESTAÑAS MODERNAS ---
# =========================================================================

tab_registro, tab_reportes, tab_historial = st.tabs(["✍️ Ingreso de Datos", "📋 Centro de Reportes y Exportación", "📈 Analítica y Dashboard Anual"])

# -------------------------------------------------------------------------
# PESTAÑA 1: REGISTRAR PROYECTO
# -------------------------------------------------------------------------
with tab_registro:
    st.markdown("### 📝 Parámetros Primarios del Nuevo Proyecto")
    
    # Uso de contenedores para dar orden visual
    with st.container():
        col_info, col_dias, col_mes, col_anio, col_fecha = st.columns([2, 1, 1, 1, 1])
        nombre_proyecto = col_info.text_input("Nombre de la Obra / Cliente", placeholder="Ej: Instalación Aroma Cacao")
        dias_trabajo = col_dias.number_input("Días Previstos", min_value=1, value=4)
        
        mes_actual_idx = datetime.date.today().month - 1
        mes_proyecto = col_mes.selectbox("Mes Contable", meses_lista, index=mes_actual_idx)
        anio_proyecto = col_anio.number_input("Año Fiscal", min_value=2020, value=datetime.date.today().year)
        fecha_obra = col_fecha.date_input("Fecha Exacta", value=datetime.date.today())

    st.write("") # Espaciador

    with st.expander("👥 1. Configuración de Mano de Obra (10 Integrantes Max)", expanded=False):
        st.info("💡 **Tip:** Puedes hacer doble clic en el nombre del rol (ej. 'Técnico 1') para escribir el nombre real de tu trabajador.")
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

    with st.expander("🚗 2. Gestión Geográfica de Costos y Viáticos", expanded=False):
        tipo_ubicacion = st.selectbox("📍 ¿Dónde se ejecutará la obra?", ["Fuera de la ciudad", "Dentro de la ciudad"])
        
        costo_viaticos_total = 0.0
        dict_viaticos_guardar = {}
        
        if tipo_ubicacion == "Fuera de la ciudad":
            st.markdown("##### 🛣️ Parámetros Foráneos (Multiplicados por el N° de personas asignadas)")
            col_v1, col_v2, col_v3, col_v4 = st.columns(4)
            
            with col_v1:
                alim_costo = st.number_input("Alimentación Costo/Día ($)", min_value=0.0, value=15.0, key="alim_c_out")
                alim_dias = st.number_input("Días Alimentación", min_value=0, value=dias_trabajo, key="alim_d_out")
            with col_v2:
                mov_costo = st.number_input("Pasajes/Movilización ($)", min_value=0.0, value=15.0, key="mov_c_out")
                mov_dias = st.number_input("Días Movilización", min_value=0, value=dias_trabajo, key="mov_d_out")
            with col_v3:
                hidra_costo = st.number_input("Hidratación Costo/Día ($)", min_value=0.0, value=10.0, key="hidra_c_out")
                hidra_dias = st.number_input("Días Hidratación", min_value=0, value=dias_trabajo, key="hidra_d_out")
            with col_v4:
                hosp_costo = st.number_input("Hospedaje Costo/Noche ($)", min_value=0.0, value=20.0, key="hosp_c_out")
                hosp_dias = st.number_input("Noches Hotel", min_value=0, value=max(0, dias_trabajo - 1), key="hosp_d_out")

            personal_activo = df_personal_editado[df_personal_editado["Asignado"] == True]
            num_personas = len(personal_activo)
            
            viatico_total_pp = (alim_costo * alim_dias) + (mov_costo * mov_dias) + (hidra_costo * hidra_dias) + (hosp_costo * hosp_dias)
            costo_viaticos_total = viatico_total_pp * num_personas
            
            dict_viaticos_guardar = {
                "Alimentación": {"costo": alim_costo, "dias": alim_dias, "tipo": "por_persona"},
                "Movilización": {"costo": mov_costo, "dias": mov_dias, "tipo": "por_persona"},
                "Hidratación": {"costo": hidra_costo, "dias": hidra_dias, "tipo": "por_persona"},
                "Hospedaje": {"costo": hosp_costo, "dias": hosp_dias, "tipo": "por_persona"}
            }
            st.success(f"**Costo Viáticos del Grupo Completo:** ${costo_viaticos_total:.2f}")

        else: 
            st.markdown("##### 🏙️ Parámetros Locales (Variables Mixtas)")
            col_dentro1, col_dentro2, col_dentro3 = st.columns(3)
            
            with col_dentro1:
                st.markdown("**Alimentación Grupal**")
                alim_costo_in = st.number_input("Costo/Día ($)", min_value=0.0, value=15.0, key="alim_c_in")
                alim_dias_in = st.number_input("Días aplicables", min_value=0, value=dias_trabajo, key="alim_d_in")
            with col_dentro2:
                st.markdown("**Movilización Fija (Global)**")
                mov_total_in = st.number_input("Costo Fijo Camioneta/Flete ($)", min_value=0.0, value=25.0, key="mov_total_in")
            with col_dentro3:
                st.markdown("**Visita / Configuración (Global)**")
                visita_config_in = st.number_input("Costo Ingeniero/Visita ($)", min_value=0.0, value=30.0, key="vis_config_in")

            personal_activo = df_personal_editado[df_personal_editado["Asignado"] == True]
            num_personas = len(personal_activo)
            
            total_alimentacion_in = alim_costo_in * alim_dias_in * num_personas
            costo_viaticos_total = total_alimentacion_in + mov_total_in + visita_config_in
            
            dict_viaticos_guardar = {
                "Alimentación": {"costo": alim_costo_in, "dias": alim_dias_in, "tipo": "por_persona"},
                "Movilización (Individual)": {"costo": mov_total_in, "dias": 1, "tipo": "individual"},
                "Visita de Configuración (Individual)": {"costo": visita_config_in, "dias": 1, "tipo": "individual"}
            }
            st.success(f"**Costo Operativo Base (Local):** ${costo_viaticos_total:.2f}")

    st.markdown("### 🛠️ 3. Ingeniería y Equipos Estructurales")
    costo_materiales = st.number_input("Costo Bruto de Materiales, Equipos o Subcontratos (Total $)", min_value=0.0, value=0.0, step=50.0)

    st.write("---")
    st.markdown("### 📈 4. Simulación Financiera y Cierre")
    
    col_pct1, col_pct2 = st.columns(2)
    pct_imprevistos = col_pct1.slider("Reserva de Riesgo / Imprevistos (%)", min_value=0, max_value=100, value=20, step=5)
    pct_ganancia_sugerida = col_pct2.slider("Margen de Utilidad Objetivo (%)", min_value=0, max_value=100, value=40, step=5)

    costo_mano_obra = personal_activo["Costo Día ($)"].sum() * dias_trabajo
    costo_directo = costo_mano_obra + costo_viaticos_total + costo_materiales
    
    reserva_imprevistos = costo_directo * (pct_imprevistos / 100)
    ganancia_calculada = costo_directo * (pct_ganancia_sugerida / 100)
    precio_sugerido = costo_directo + reserva_imprevistos + ganancia_calculada

    # Recuadro gris claro elegante provisto por st.info
    st.info(f"💡 Precio Base Recomendado por el algoritmo: **${precio_sugerido:,.2f}** (Sin IVA)")
    
    precio_venta_final = st.number_input(
        "Ajuste Comercial Manual: Cierra tu Precio de Venta Real ($)", 
        min_value=0.0, 
        value=float(precio_sugerido), 
        step=10.0
    )

    ganancia_real = precio_venta_final - costo_directo - reserva_imprevistos
    iva_monto = precio_venta_final * 0.15
    precio_total_con_iva = precio_venta_final + iva_monto

    # Este bloque renderizará las Tarjetas "Cards" gracias al CSS personalizado superior
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("Costo Directo Ejecutado", f"${costo_directo:,.2f}")
    col_s2.metric(f"Fondo de Riesgo ({pct_imprevistos}%)", f"${reserva_imprevistos:,.2f}")
    col_s3.metric("Utilidad Neta (Ganancia)", f"${ganancia_real:,.2f}")
    col_s4.metric("Facturación Base", f"${precio_venta_final:,.2f}")

    st.write("")
    
    # Usar columnas para centrar el botón de guardar y darle protagonismo
    c_btn1, c_btn2, c_btn3 = st.columns([1,2,1])
    with c_btn2:
        if st.button("💾 CONFIRMAR Y REGISTRAR PROYECTO", type="primary", use_container_width=True):
            if nombre_proyecto:
                nombres_existentes = [p["Proyecto"] for p in st.session_state.proyectos]
                if nombre_proyecto in nombres_existentes:
                    st.error("Error: Ya existe una obra registrada bajo este nombre. Usa un identificador único.")
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
                        "_Materiales": costo_materiales
                    })
                    guardar_en_base_de_datos(st.session_state.proyectos)
                    st.success("✅ ¡Operación exitosa! Datos encriptados y guardados localmente.")
                    st.rerun()
            else:
                st.error("⚠️ Debes proporcionar un nombre al proyecto para poder registrarlo.")

# -------------------------------------------------------------------------
# PESTAÑA 2: CONSULTAR Y EXPORTAR REPORTES
# -------------------------------------------------------------------------
with tab_reportes:
    if st.session_state.proyectos:
        datos_publicos = [{k: v for k, v in p.items() if not k.startswith("_")} for p in st.session_state.proyectos]
        df_resultados = pd.DataFrame(datos_publicos).fillna(0)
        
        columnas_ordenadas = ["Año", "Mes", "Fecha", "Proyecto", "Costo Directo", "Fondo Imprevistos", "Ganancia Neta", "PRECIO VENTA FINAL", "IVA (15%)", "PRECIO TOTAL"]
        df_resultados = df_resultados[[col for col in columnas_ordenadas if col in df_resultados.columns]]
        formato_moneda = {col: "${:,.2f}" for col in df_resultados.columns if col not in ["Mes", "Proyecto", "Año", "Fecha"]}

        st.markdown("### 🖨️ Centro de Mando: Impresión de Documentos")
        
        # Opciones más amigables visualmente en horizontal
        tipo_reporte = st.radio(
            "Selecciona el motor de extracción:",
            ["📑 Cierre Mensual (Filtrar un Mes)", "📚 Auditoría Anual (Todos los Registros)", "👤 Cotización Comercial (Un solo Proyecto)"],
            horizontal=True
        )
        st.write("---")

        col_rep1, col_rep2 = st.columns([1, 2])

        if tipo_reporte == "📑 Cierre Mensual (Filtrar un Mes)":
            with col_rep1:
                meses_disponibles = list(set([p["Mes"] for p in st.session_state.proyectos]))
                meses_ordenados = sorted(meses_disponibles, key=lambda x: meses_lista.index(x))
                mes_seleccionado = st.selectbox("📅 Selecciona el Mes:", meses_ordenados)
                
            with col_rep2:
                st.markdown(f"**Vista Rápida: {mes_seleccionado}**")
                lista_a_exportar = [p for p in st.session_state.proyectos if p["Mes"] == mes_seleccionado]
                df_a_exportar = df_resultados[df_resultados["Mes"] == mes_seleccionado]
                st.dataframe(df_a_exportar.style.format(formato_moneda), use_container_width=True, hide_index=True)
                
                titulo_doc = f"REPORTE INTERNO DE CONTABILIDAD - {mes_seleccionado.upper()}"
                nombre_archivo = f"Balance_Mensual_{mes_seleccionado}.pdf"
                pdf_mes = generar_pdf(lista_a_exportar, df_a_exportar, tipo_exportacion="todos", titulo_reporte=titulo_doc)
                
                st.download_button(
                    label=f"📥 Generar y Descargar PDF del Mes",
                    data=pdf_mes, file_name=nombre_archivo, mime="application/pdf", type="primary", use_container_width=True
                )

        elif tipo_reporte == "📚 Auditoría Anual (Todos los Registros)":
            st.markdown("#### 🗓️ Base de Datos Completa")
            st.dataframe(df_resultados.style.format(formato_moneda), use_container_width=True, hide_index=True)
            
            titulo_doc = "REPORTE INTERNO DE CONTABILIDAD ENERO A DICIEMBRE"
            nombre_archivo = "Auditoria_Anual_Latitud_Solar.pdf"
            pdf_anual = generar_pdf(st.session_state.proyectos, df_resultados, tipo_exportacion="todos", titulo_reporte=titulo_doc)
            
            st.write("")
            col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
            with col_btn2:
                st.download_button(
                    label="📥 Exportar Auditoría Completa (Enero - Diciembre)",
                    data=pdf_anual, file_name=nombre_archivo, mime="application/pdf", type="primary", use_container_width=True
                )
            
        elif tipo_reporte == "👤 Cotización Comercial (Un solo Proyecto)":
            with col_rep1:
                nombres_proyectos = [p["Proyecto"] for p in st.session_state.proyectos]
                proyecto_seleccionado = st.selectbox("📂 Buscar y Seleccionar Obra:", nombres_proyectos)
            
            with col_rep2:
                st.markdown(f"**Inspección del Proyecto:** {proyecto_seleccionado}")
                lista_a_exportar = [p for p in st.session_state.proyectos if p["Proyecto"] == proyecto_seleccionado]
                df_a_exportar = df_resultados[df_resultados["Proyecto"] == proyecto_seleccionado]
                st.dataframe(df_a_exportar.style.format(formato_moneda), use_container_width=True, hide_index=True)
                
                nombre_archivo = f"Cotizacion_{proyecto_seleccionado.replace(' ', '_')}.pdf"
                pdf_individual = generar_pdf(lista_a_exportar, df_a_exportar, tipo_exportacion="individual")
                
                st.download_button(
                    label=f"📄 Emitir Formato PDF (Para Cliente y Archivo)",
                    data=pdf_individual, file_name=nombre_archivo, mime="application/pdf", type="primary", use_container_width=True
                )

        st.write("---")
        with st.expander("⚠️ Configuración Avanzada: Depurar Errores (Eliminar Proyectos)"):
            st.error("Las acciones en esta sección son permanentes e irreversibles.")
            nombres_proyectos_del = [p["Proyecto"] for p in st.session_state.proyectos]
            proyecto_a_eliminar = st.selectbox("Localiza el proyecto a destruir:", nombres_proyectos_del, key="del_proj_box")
            
            if st.button("🗑️ Eliminar Definitivamente", type="secondary"):
                st.session_state.proyectos = [p for p in st.session_state.proyectos if p["Proyecto"] != proyecto_a_eliminar]
                guardar_en_base_de_datos(st.session_state.proyectos)
                st.warning(f"Protocolo ejecutado: '{proyecto_a_eliminar}' fue eliminado.")
                st.rerun()
    else:
        st.info("⚠️ Tu base de datos está vacía. Registra proyectos para activar esta sección.")

# -------------------------------------------------------------------------
# PESTAÑA 3: HISTORIAL GLOBAL ANUAL Y DASHBOARD
# -------------------------------------------------------------------------
with tab_historial:
    if st.session_state.proyectos:
        st.markdown("### 📈 Panel Analítico de Rendimiento (Dashboard)")
        st.write("Mapeo consolidado del crecimiento, la inversión y el comportamiento financiero del año en curso.")
        
        df_global = pd.DataFrame([{k: v for k, v in p.items() if not k.startswith("_")} for p in st.session_state.proyectos]).fillna(0)
        df_global["Costo Operativo"] = df_global["Costo Directo"] + df_global["Fondo Imprevistos"]
        
        resumen_mensual = df_global.groupby("Mes")[["Costo Operativo", "Ganancia Neta", "IVA (15%)", "PRECIO TOTAL"]].sum().reset_index()
        resumen_mensual["Mes_Num"] = resumen_mensual["Mes"].apply(lambda x: meses_lista.index(x) if x in meses_lista else 99)
        resumen_mensual = resumen_mensual.sort_values("Mes_Num").drop("Mes_Num", axis=1)
        
        # Envolviendo en un expander si es muy grande, o dejarlo visible. Al ser resumen mensual, ocupa poco espacio
        st.dataframe(resumen_mensual.style.format({
            "Costo Operativo": "${:,.2f}",
            "Ganancia Neta": "${:,.2f}",
            "IVA (15%)": "${:,.2f}",
            "PRECIO TOTAL": "${:,.2f}"
        }), use_container_width=True, hide_index=True)
        
        t_costo = resumen_mensual["Costo Operativo"].sum()
        t_ganancia = resumen_mensual["Ganancia Neta"].sum()
        t_iva = resumen_mensual["IVA (15%)"].sum()
        t_facturado = resumen_mensual["PRECIO TOTAL"].sum()
        
        st.write("---")
        st.markdown("#### 🏆 KPIs: Estados Financieros Acumulados")
        
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        col_t1.metric("🔴 Inversión y Egresos (Costos)", f"${t_costo:,.2f}")
        col_t2.metric("🟢 Utilidad Neta (Ganancia)", f"${t_ganancia:,.2f}")
        col_t3.metric("🟠 Impuestos Retenidos (IVA)", f"${t_iva:,.2f}")
        col_t4.metric("🔵 Facturación Bruta (Ingreso Total)", f"${t_facturado:,.2f}")
    else:
        st.info("⚠️ Tu base de datos está vacía. Registra proyectos para alimentar el Dashboard.")
