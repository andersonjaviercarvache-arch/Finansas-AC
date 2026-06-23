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

# --- CÁLCULO REACTIVO PARA LA SUGERENCIA ---
st.subheader("4. Sugerencia de Precio")

# La app calcula todo en tiempo real
personal_activo = df_personal_editado[df_personal_editado["Asignado"] == True]
num_personas = len(personal_activo)

costo_mano_obra = personal_activo["Costo Día ($)"].sum() * dias_trabajo
costo_viaticos_total = viatico_diario_pp * num_personas * dias_trabajo
costo_directo = costo_mano_obra + costo_viaticos_total + costo_materiales

reserva_imprevistos = costo_directo * 0.20
ganancia_esperada = costo_directo * 0.40

# Sugerencia calculada
precio_sugerido = costo_directo + reserva_imprevistos + ganancia_esperada

# Mostrar desglose en tiempo real
col_s1, col_s2, col_s3, col_s4 = st.columns(4)
col_s1.metric("Costo Directo", f"${costo_directo:,.2f}")
col_s2.metric("Imprevistos (20%)", f"${reserva_imprevistos:,.2f}")
col_s3.metric("Ganancia Base (40%)", f"${ganancia_esperada:,.2f}")
col_s4.metric("PRECIO SUGERIDO", f"${precio_sugerido:,.2f}")

st.info(f"💡 Según tu estructura de costos, te sugerimos cobrar un mínimo de **${precio_sugerido:,.2f}**.")

# 5. Definición del Precio Final y Guardado
st.write("¿Deseas redondear o ajustar este precio para tu cliente?")
precio_final = st.number_input("Ingresa el Precio Final de Venta ($)", min_value=0.0, value=float(precio_sugerido), step=10.0)

if st.button("Guardar Proyecto en el Mes", type="primary"):
    if nombre_proyecto:
        # Calculamos la utilidad real basada en el precio que finalmente decidiste cobrar
        utilidad_real = precio_final - costo_directo - reserva_imprevistos
        
        st.session_state.proyectos.append({
            "Proyecto": nombre_proyecto,
            "Costo Directo": costo_directo,
            "Imprevistos (20%)": reserva_imprevistos,
            "Precio Sugerido": precio_sugerido,
            "PRECIO VENTA": precio_final,
            "Utilidad Real": utilidad_real
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
    
    # Formato visual
    df_mostrar = df_resultados.style.format({
        "Costo Directo": "${:,.2f}",
        "Imprevistos (20%)": "${:,.2f}",
        "Precio Sugerido": "${:,.2f}",
        "PRECIO VENTA": "${:,.2f}",
        "Utilidad Real": "${:,.2f}"
    })
    
    st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
    
    # Sumatorias
    total_costos = df_resultados["Costo Directo"].sum()
    total_imprevistos = df_resultados["Imprevistos (20%)"].sum()
    total_utilidad = df_resultados["Utilidad Real"].sum()
    total_facturacion = df_resultados["PRECIO VENTA"].sum()
    
    # Tarjetas resumen
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Gastos Directos", f"${total_costos:,.2f}")
    col_m2.metric("Fondo de Emergencias", f"${total_imprevistos:,.2f}")
    col_m3.metric("Utilidad Neta Real", f"${total_utilidad:,.2f}")
    col_m4.metric("Facturación Total", f"${total_facturacion:,.2f}")
else:
    st.info("Aún no tienes proyectos guardados. Configura uno en la parte superior y presiona 'Guardar Proyecto'.")
