import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestor de Rentabilidad", layout="wide")

st.title("📊 Gestor Financiero - Latitud Solar")

# Sidebar para Gastos Fijos
st.sidebar.header("Configuración de Empresa")
gastos_fijos = st.sidebar.number_input("Gastos Fijos Mensuales ($)", value=4956)

# Formulario para agregar proyectos
st.header("Registrar Proyecto")
with st.form("nuevo_proyecto"):
    col1, col2 = st.columns(2)
    nombre = col1.text_input("Nombre del Proyecto")
    costo = col2.number_input("Costo Directo ($)", min_value=0.0)
    submit = st.form_submit_button("Agregar")

if 'proyectos' not in st.session_state:
    st.session_state.proyectos = []

if submit:
    # Lógica de márgenes
    if costo < 1000: margen = 0.50
    elif costo < 10000: margen = 0.35
    else: margen = 0.25
    
    st.session_state.proyectos.append({
        "Proyecto": nombre,
        "Costo": costo,
        "Precio Venta": costo * (1 + margen),
        "Utilidad": costo * margen
    })

# Mostrar tabla y resultados
if st.session_state.proyectos:
    df = pd.DataFrame(st.session_state.proyectos)
    st.table(df)
    
    total_utilidad = df["Utilidad"].sum()
    balance = total_utilidad - gastos_fijos
    
    st.metric("Utilidad Bruta Total", f"${total_utilidad:,.2f}")
    st.metric("Balance Final (Utilidad - Gastos Fijos)", f"${balance:,.2f}", delta_color="normal")
