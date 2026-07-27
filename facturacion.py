import streamlit as st
import pandas as pd
from datetime import datetime

def render():
    """Módulo de Facturación Electrónica (DTE) para El Salvador"""
    st.subheader("🧾 Emisión y Control de Documentos Tributarios Electrónicos (DTE)")
    
    # Sub-pestañas para organizar la operación
    tab1, tab2, tab3 = st.tabs(["Emisión de DTE", "Historial y Sello", "Configuración Emisor"])
    
    with tab1:
        st.markdown("### Generar Nuevo Documento")
        
        col1, col2 = st.columns(2)
        with col1:
            tipo_dte = st.selectbox(
                "Tipo de DTE",
                ["01 - Factura", "03 - Comprobante de Crédito Fiscal (CCF)", "14 - Factura de Sujeto Excluido", "05 - Nota de Crédito"]
            )
            cliente_nombre = st.text_input("Nombre / Razón Social del Receptor")
            cliente_nit = st.text_input("NIT / DUI / NRC del Receptor")
            
        with col2:
            fecha_emision = st.date_input("Fecha de Emisión", datetime.now())
            condicion_operacion = st.selectbox("Condición de la Operación", ["Contado", "Crédito", "Otro"])
            
        st.markdown("---")
        st.markdown("#### Detalle de Ítems / Productos")
        
        # Simulación de tabla interactiva para ítems
        if "items_dte" not in st.session_state:
            st.session_state.items_dte = pd.DataFrame(columns=["Cantidad", "Descripción", "Precio Unitario", "Ventas Gravadas"])
            
        with st.form("form_item"):
            c1, c2, c3 = st.columns([1, 3, 1])
            cant = c1.number_input("Cantidad", min_value=1.0, value=1.0)
            desc = c2.text_input("Descripción del bien o servicio")
            precio = c3.number_input("Precio Unitario ($)", min_value=0.0, value=0.0)
            
            add_item = st.form_submit_button("Agregar Ítem al DTE")
            if add_item and desc:
                subtotal = cant * precio
                nuevo_row = pd.DataFrame([[cant, desc, precio, subtotal]], columns=["Cantidad", "Descripción", "Precio Unitario", "Ventas Gravadas"])
                st.session_state.items_dte = pd.concat([st.session_state.items_dte, nuevo_row], ignore_index=True)
                st.rerun()
                
        if not st.session_state.items_dte.empty:
            st.dataframe(st.session_state.items_dte, use_container_width=True)
            
            total_gravado = st.session_state.items_dte["Ventas Gravadas"].sum()
            iva = total_gravado * 0.13 if "CCF" in tipo_dte else 0.0 # IVA estimado 13% si aplica
            total_pagar = total_gravado + iva if "CCF" in tipo_dte else total_gravado
            
            st.markdown(f"**Subtotal Gravado:** ${total_gravado:,.2f}")
            if "CCF" in tipo_dte:
            	st.markdown(f"**IVA (13%):** ${iva:,.2f}")
            st.markdown(f"### **Total a Pagar: ${total_pagar:,.2f}**")
            
            if st.button("Transmitir DTE (Simulación Hacienda)"):
                st.success("¡DTE generado y transmitido exitosamente con Sello de Recepción!")
                st.balloons()
        else:
            st.info("Agregue al menos un ítem para calcular el total del documento.")

    with tab2:
        st.markdown("### Historial de Documentos Emitidos")
        st.write("Consulta, descarga de JSON/PDF y validación de DTEs previos.")
        # Placeholder para historial
        
    with tab3:
        st.markdown("### Parámetros de Transmisión y Credenciales")
        st.text_input("API Key / Token MH", type="password")
        st.text_input("Código de Establecimiento", value="M001")
        st.text_input("Punto de Venta", value="P001")