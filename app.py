import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestor de Rentabilidad", layout="wide")

st.title("📊 Gestor Financiero - Latitud Solar")

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

# Tabla interactiva
df_personal_base = pd.DataFrame([
    {"Rol": "Supervisor", "Costo Día ($)": 50.00, "Asignado": True},
    {"Rol": "Técnico 1", "Costo Día ($)": 37.50, "Asignado": True},
    {"Rol": "Técnico 2", "Costo Día ($)": 37.50, "Asignado": True},
    {"Rol": "Ayudante", "Costo Día ($)": 25.00, "Asignado": False}
])
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
if st.button("Calcular Precio de Venta Ideal", type="primary"):
    if nombre_proyecto:
        # Filtrar solo el personal que fue marcado como "Asignado"
        personal_activo = df_personal_editado[df_personal_editado["Asignado"] == True]
        num_personas = len(personal_activo)
        
        # Matemáticas del Costo Directo
        costo_mano_obra = personal_activo["Costo Día ($)"].sum() * dias_trabajo
        costo_viaticos_total = viatico_diario_pp * num_personas * dias_trabajo
        costo_directo = costo_mano_obra + costo_viaticos_total + costo_materiales
        
        # Cálculo de Márgenes (40% Ganancia, 20% Imprevistos)
        porcentaje_imprevistos = 0.20
        porcentaje_ganancia = 0.40
        
        reserva_imprevistos = costo_directo * porcentaje_imprevistos
        ganancia_neta = costo_directo * porcentaje_ganancia
        
        # Precio final sugerido
        precio_venta = costo_directo + reserva_imprevistos + ganancia_neta
        
        # Guardar en memoria
        st.session_state.proyectos.append({
            "Proyecto": nombre_proyecto,
            "Costo Directo": costo_directo,
            "Fondo Imprevistos (20%)": reserva_imprevistos,
            "Ganancia Neta (40%)": ganancia_neta,
            "PRECIO VENTA IDEAL": precio_venta
        })
        st.success(f"Proyecto '{nombre_proyecto}' procesado. El precio sugerido para el cliente es de ${precio_venta:,.2f}")
    else:
        st.error("Por favor, ingresa un nombre para el proyecto antes de continuar.")

# --- SECCIÓN: REPORTE MENSUAL ---
st.write("---")
st.header("Reporte de Proyectos y Proyecciones")

if st.session_state.proyectos:
    # Crear y mostrar tabla resumen
    df_resultados = pd.DataFrame(st.session_state.proyectos)
    
    # Formatear a moneda para mejor lectura
    df_mostrar = df_resultados.style.format({
        "Costo Directo": "${:,.2f}",
        "Fondo Imprevistos (20%)": "${:,.2f}",
        "Ganancia Neta (40%)": "${:,.2f}",
        "PRECIO VENTA IDEAL": "${:,.2f}"
    })
    
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    
    # Cálculos finales para las métricas
    total_costos = df_resultados["Costo Directo"].sum()
    total_imprevistos = df_resultados["Fondo Imprevistos (20%)"].sum()
    total_ganancias = df_resultados["Ganancia Neta (40%)"].sum()
    total_facturacion = df_resultados["PRECIO VENTA IDEAL"].sum()
    
    # Tarjetas de indicadores
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Costos Operativos", f"${total_costos:,.2f}")
    col_m2.metric("Fondo de Imprevistos", f"${total_imprevistos:,.2f}")
    col_m3.metric("Ganancia Total", f"${total_ganancias:,.2f}")
    col_m4.metric("Facturación Proyectada", f"${total_facturacion:,.2f}")
        
else:
    st.info("No hay proyectos registrados en este momento. Ingresa los datos arriba para comenzar.")
