import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestor de Rentabilidad", layout="wide")

st.title("📊 Gestor Financiero - Latitud Solar")

# --- CONFIGURACIÓN DE EMPRESA ---
st.sidebar.header("Configuración de Empresa")
gastos_fijos = st.sidebar.number_input("Gastos Fijos Mensuales ($)", value=4956.0, step=100.0)

# --- INICIALIZAR MEMORIA ---
if 'proyectos' not in st.session_state:
    st.session_state.proyectos = []

# --- SECCIÓN: REGISTRO DE PROYECTO ---
st.header("Registrar Nuevo Proyecto")

# 1. Datos Generales
col_info, col_dias = st.columns(2)
nombre_proyecto = col_info.text_input("Nombre del Proyecto")
dias_trabajo = col_dias.number_input("Días de Trabajo en Obra", min_value=1, value=4)

st.write("---")

# 2. Personal y Mano de Obra
st.subheader("1. Costos de Personal (Por Día)")
st.write("Edita la tarifa o marca la casilla 'Asignado' para incluir al trabajador en esta obra.")

# Tabla interactiva por defecto
df_personal_base = pd.DataFrame([
    {"Rol": "Supervisor", "Costo Día ($)": 50.00, "Asignado": True},
    {"Rol": "Técnico 1", "Costo Día ($)": 37.50, "Asignado": True},
    {"Rol": "Técnico 2", "Costo Día ($)": 37.50, "Asignado": True},
    {"Rol": "Ayudante", "Costo Día ($)": 25.00, "Asignado": False}
])
# El usuario puede editar esta tabla en vivo en la aplicación
df_personal_editado = st.data_editor(df_personal_base, use_container_width=True, hide_index=True)

st.write("---")

# 3. Desglose de Viáticos
st.subheader("2. Desglose de Viáticos Diarios (Por Persona)")
col_v1, col_v2, col_v3 = st.columns(3)
alim = col_v1.number_input("Alimentación ($)", min_value=0.0, value=15.0)
mov = col_v2.number_input("Movilización ($)", min_value=0.0, value=15.0)
hidra = col_v3.number_input("Hidratación ($)", min_value=0.0, value=10.0)

viatico_diario_pp = alim + mov + hidra
st.info(f"**Total viáticos por persona al día:** ${viatico_diario_pp:.2f}")

st.write("---")

# 4. Materiales Adicionales
st.subheader("3. Materiales y Otros")
costo_materiales = st.number_input("Costo de Materiales o Equipos ($)", min_value=0.0, value=0.0, step=50.0)

# 5. Botón de Procesamiento
if st.button("Calcular y Agregar Proyecto al Mes", type="primary"):
    if nombre_proyecto:
        # Filtrar solo el personal que fue marcado como "Asignado"
        personal_activo = df_personal_editado[df_personal_editado["Asignado"] == True]
        num_personas = len(personal_activo)
        
        # Matemáticas del Costo Directo
        costo_mano_obra = personal_activo["Costo Día ($)"].sum() * dias_trabajo
        costo_viaticos_total = viatico_diario_pp * num_personas * dias_trabajo
        costo_directo = costo_mano_obra + costo_viaticos_total + costo_materiales
        
        # Aplicación del modelo de márgenes variables
        if costo_directo < 1000: margen = 0.50
        elif costo_directo < 10000: margen = 0.35
        else: margen = 0.25
        
        precio_venta = costo_directo * (1 + margen)
        utilidad = precio_venta - costo_directo
        
        # Guardar en memoria
        st.session_state.proyectos.append({
            "Proyecto": nombre_proyecto,
            "Costo Personal": costo_mano_obra,
            "Costo Viáticos": costo_viaticos_total,
            "Materiales": costo_materiales,
            "COSTO TOTAL": costo_directo,
            "PRECIO VENTA": precio_venta,
            "Utilidad Neta": utilidad
        })
        st.success(f"Proyecto '{nombre_proyecto}' procesado exitosamente.")
    else:
        st.error("Por favor, ingresa un nombre para el proyecto antes de continuar.")

# --- SECCIÓN: REPORTE MENSUAL ---
st.write("---")
st.header("Reporte de Rentabilidad del Mes")

if st.session_state.proyectos:
    # Crear y mostrar tabla resumen
    df_resultados = pd.DataFrame(st.session_state.proyectos)
    
    # Formatear a moneda para mejor lectura
    df_mostrar = df_resultados.style.format({
        "Costo Personal": "${:,.2f}",
        "Costo Viáticos": "${:,.2f}",
        "Materiales": "${:,.2f}",
        "COSTO TOTAL": "${:,.2f}",
        "PRECIO VENTA": "${:,.2f}",
        "Utilidad Neta": "${:,.2f}"
    })
    
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    
    # Cálculos finales
    total_utilidad = df_resultados["Utilidad Neta"].sum()
    balance = total_utilidad - gastos_fijos
    
    # Tarjetas de indicadores
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Gastos Fijos", f"${gastos_fijos:,.2f}")
    col_m2.metric("Utilidad Generada", f"${total_utilidad:,.2f}")
    
    # El balance final se pinta verde/rojo según si hay ganancias o pérdidas
    if balance >= 0:
        col_m3.metric("Ganancia Real (Caja)", f"${balance:,.2f}", "Rentable")
    else:
        col_m3.metric("Déficit (Falta Facturar)", f"${balance:,.2f}", "-Pérdida")
        
else:
    st.info("No hay proyectos registrados en este momento. Ingresa los datos arriba para comenzar.")
