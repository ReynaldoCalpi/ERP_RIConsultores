import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración inicial de la página
st.set_page_config(
    page_title="RI ERP Cloud",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar variables de estado para la sesión
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "items_dte" not in st.session_state:
    st.session_state.items_dte = pd.DataFrame(columns=["Cantidad", "Descripción", "Precio Unitario", "Ventas Gravadas"])

def login_screen():
    """Módulo de Autenticación exclusivo para clientes de la firma"""
    st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>RI Consultores - ERP Cloud</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280;'>Sistema Integral de Gestión Empresarial y Tributaria</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("Acceso al Sistema")
            user = st.text_input("Usuario / NIT o Empresa")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Ingresar")
            
            if submit:
                if user and password: 
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("Por favor, ingrese sus credenciales.")

def render_facturacion():
    """Módulo de Facturación Electrónica (DTE) integrado"""
    st.subheader("🧾 Emisión y Control de Documentos Tributarios Electrónicos (DTE)")
    
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
            iva = total_gravado * 0.13 if "CCF" in tipo_dte else 0.0 
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
        
    with tab3:
        st.markdown("### Parámetros de Transmisión y Credenciales")
        st.text_input("API Key / Token MH", type="password")
        st.text_input("Código de Establecimiento", value="M001")
        st.text_input("Punto de Venta", value="P001")

def main_dashboard():
    """Panel principal del ERP una vez autenticado"""
    st.sidebar.title("RI Consultores")
    st.sidebar.markdown(f"**Usuario:** {st.session_state.username}")
    st.sidebar.markdown("---")
    
    menu = st.sidebar.radio(
        "Navegación Principal",
        ["Inicio", "Contabilidad", "Facturación DTE", "Planillas", "Inventarios y Activo Fijo"]
    )
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
        
    # Enrutamiento de Módulos
    if menu == "Inicio":
        st.title("Panel de Control General")
        st.info("Bienvenido al núcleo de gestión integral. Seleccione un módulo en el menú lateral para comenzar.")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ventas del Mes", "$0.00", "0%")
        col2.metric("IVA por Pagar", "$0.00", "$0.00")
        col3.metric("Planilla Activa", "$0.00", "0 empleados")
        col4.metric("Activos Registrados", "0", "OK")

    elif menu == "Contabilidad":
        st.title("Módulo de Contabilidad")
        st.write("Gestión de partida doble, libro diario y estados financieros adaptados a normativa local.")
        
    elif menu == "Facturación DTE":
        render_facturacion()
        
    elif menu == "Planillas":
        st.title("Cálculo de Planillas")
        st.write("Procesamiento de salarios, retenciones de renta, ISSS y AFP.")
        
    elif menu == "Inventarios y Activo Fijo":
        st.title("Inventarios y Activo Fijo")
        st.write("Control de existencias y generación de viñetas de identificación de activos.")

# Control de flujo principal
if not st.session_state.authenticated:
    login_screen()
else:
    main_dashboard()
