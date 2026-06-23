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
st.info(f"**Total viáticos diarios por persona:** ${viatico_diario_pp:.2f}")

st.write("---")

# 4. Materiales Adicionales
st.subheader("3. Materiales y Otros")
costo_materiales = st.number_input("Costo de Materiales o Equipos ($)", min_value=0.0, value=0.0, step=50.0)

st.write("---")

# --- CÁLCULO DE MÁRGENES Y PRECIO FINAL ---
st.subheader("4. Ajuste de Márgenes y Precio de Venta")

# Controles para ajustar los porcentajes (puedes bajarlos a 0 o subirlos a tu gusto)
col_pct1, col_pct2 = st.columns(2)
pct_imprevistos = col_pct1.slider("Porcentaje para Imprevistos (%)", min_value=0, max_value=100, value=20, step=5)
pct_ganancia = col_pct2.slider("Porcentaje de Ganancia (%)", min_value=0, max_value=100, value=40, step=5)

# Cálculos matemáticos en tiempo real
personal_activo = df_personal_editado[df_personal_editado["Asignado"] == True]
num_personas = len(personal_activo)

costo_mano_obra = personal_activo["Costo Día ($)"].sum() * dias_trabajo
costo_viaticos_total = viatico_diario_pp * num_personas * dias_trabajo
costo_directo = costo_mano_obra + costo_viaticos_total + costo_materiales

reserva_imprevistos = costo_directo * (pct_imprevistos / 100)
ganancia_esperada = costo_directo * (pct_ganancia / 100)

# PRECIO DE VENTA FINAL (Sin IVA)
precio_venta_final = costo_directo + reserva_imprevistos + ganancia_esperada

# CÁLCULO DEL IVA (15%) Y PRECIO TOTAL
iva_monto = precio_venta_final * 0.15
precio_total_con_iva = precio_venta_final + iva_monto

# Mostrar desglose en pantalla
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
col_s1.metric("Costo Directo", f"${costo_directo:,.2f}")
col_s2.metric(f"Imprevistos ({pct_imprevistos}%)", f"${reserva_imprevistos:,.2f}")
col_s3.metric(f"Ganancia ({pct_ganancia}%)", f"${ganancia_esperada:,.2f}")
col_s4.metric("PRECIO DE VENTA FINAL", f"${precio_venta_final:,.2f}")

# Mostrar cuadro final con Impuestos
st.success(f"**PRECIO DE VENTA FINAL:** ${precio_venta_final:,.2f}  |  **IVA (15%):** ${iva_monto:,.2f}  |  **PRECIO TOTAL:** ${precio_total_con_iva:,.2f}")

# Botón para guardar el proyecto en el registro mensual
if st.button("Guardar Proyecto en el Mes", type="primary"):
    if nombre_proyecto:
        st.session_state.proyectos.append({
            "Proyecto": nombre_proyecto,
            "Costo Directo": costo_directo,
            f"Imprevistos ({pct_imprevistos}%)": reserva_imprevistos,
            f"Ganancia ({pct_ganancia}%)": ganancia_esperada,
            "PRECIO VENTA FINAL": precio_venta_final,
            "IVA (15%)": iva_monto,
            "PRECIO TOTAL": precio_total_con_iva
        })
        st.success(f"Proyecto '{nombre_proyecto}' registrado exitosamente.")
    else:
        st.error("Por favor, ingresa el nombre del proyecto en la parte superior.")

# --- SECCIÓN: REPORTE MENSUAL ---
st.write("---")
st.header("Reporte Mensual de Facturación")

if st.session_state.proyectos:
    # Crear y mostrar tabla resumen
    df_resultados = pd.DataFrame(st.session_state.proyectos)
    
    # Formato visual para que se vea como moneda
    formato_moneda = {col: "${:,.2f}" for col in df_resultados.columns if col != "Proyecto"}
    df_mostrar = df_resultados.style.format(formato_moneda)
    
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    
    # Sumatorias para las tarjetas finales
    total_costos = df_resultados["Costo Directo"].sum()
    
    # Manejar las sumatorias dinámicas de imprevistos y ganancias (por si cambian los porcentajes entre proyectos)
    cols_imprevistos = [col for col in df_resultados.columns if "Imprevistos" in col]
    cols_ganancias = [col for col in df_resultados.columns if "Ganancia" in col]
    
    total_imprevistos = df_resultados[cols_imprevistos].sum().sum()
    total_utilidad = df_resultados[cols_ganancias].sum().sum()
    
    total_venta_final = df_resultados["PRECIO VENTA FINAL"].sum()
    total_iva = df_resultados["IVA (15%)"].sum()
    total_recaudado = df_resultados["PRECIO TOTAL"].sum()
    
    # Tarjetas resumen
    st.subheader("Resumen General")
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Total Costos Directos", f"${total_costos:,.2f}")
    col_m2.metric("Total Fondo Emergencias", f"${total_imprevistos:,.2f}")
    col_m3.metric("Total Ganancia Neta", f"${total_utilidad:,.2f}")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    col_t1.metric("Subtotal (Venta Final)", f"${total_venta_final:,.2f}")
    col_t2.metric("IVA por Declarar", f"${total_iva:,.2f}")
    col_t3.metric("Total a Cobrar a Clientes", f"${total_recaudado:,.2f}")
else:
    st.info("Aún no tienes proyectos guardados. Configura uno en la parte superior y presiona 'Guardar Proyecto'.")
