import streamlit as st

# Configuración inicial de la página (Debe ser el primer comando de Streamlit)
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
                # Validación preliminar (hardcodeada temporalmente para pruebas de arquitectura)
                if user and password: 
                    st.session_state.authenticated = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("Por favor, ingrese sus credenciales.")

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
        
        # Métricas de ejemplo (Mockups iniciales)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Ventas del Mes", "$0.00", "0%")
        col2.metric("IVA por Pagar", "$0.00", "$0.00")
        col3.metric("Planilla Activa", "$0.00", "0 empleados")
        col4.metric("Activos Registrados", "0", "OK")

    elif menu == "Contabilidad":
        st.title("Módulo de Contabilidad")
        st.write("Gestión de partida doble, libro diario y estados financieros adaptados a normativa local.")
        
    elif menu == "Facturación DTE":
        st.title("Facturación Electrónica (DTE)")
        st.write("Emisión, control y registro de Documentos Tributarios Electrónicos.")
        
    elif menu == "Planillas":
        st.title("Cálculo de Planillas")
        st.write("Procesamiento de salarios, retenciones de renta, ISSS y AFP.")
        
    elif menu == "Inventarios y Activo Fijo":
        st.title("Inventarios y Activo Fijo")
        st.write("Control de existencias y generación de viñetas de identificación de activos.")

# Control de flujo principal según estado de sesión
if not st.session_state.authenticated:
    login_screen()
else:
    main_dashboard()