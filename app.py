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
            
            # Soporte para registros guardados antes de esta actualización (evita errores en datos viejos)
            if p.get('_Traslado', 0.0) > 0 and "Traslado de Equipos" not in p["_Viaticos"]:
                pdf.set_font("Helvetica", '', 9)
                pdf.cell(0, 6, f"Traslado de Equipos (Histórico): ${p.get('_Traslado', 0.0):,.2f}", new_x="LMARGIN", new_y="NEXT")
                
            pdf.set_font("Helvetica", '', 9)
            pdf.cell(0, 6, f"Materiales y Otros Costos: ${p.get('_Materiales', 0.0):,.2f}", new_x="LMARGIN", new_y="NEXT")
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
        pdf.cell(40, 6, f"${sum_venta
