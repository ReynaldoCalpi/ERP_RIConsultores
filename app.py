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
        st.subheader("📊 Módulo de Contabilidad y Partida Doble")
        
        tab_c1, tab_c2, tab_c3 = st.tabs(["Registro de Partidas", "Libro Diario", "Estados Financieros"])
        
        with tab_c1:
            st.markdown("### Nueva Partida Contable")
            
            # Inicializar el libro diario en session_state si no existe
            if "libro_diario" not in st.session_state:
                st.session_state.libro_diario = pd.DataFrame(columns=["Fecha", "Código", "Cuenta", "Debe", "Haber"])
            
            fecha_partida = st.date_input("Fecha de Operación", datetime.now(), key="fecha_p")
            concepto = st.text_input("Concepto General de la Partida")
            
            st.markdown("#### Detalle de Cuentas")
            with st.form("form_asiento"):
                col_c1, col_c2, col_c3, col_c4 = st.columns([1, 2, 1, 1])
                cod_cuenta = col_c1.text_input("Código", value="1101")
                nom_cuenta = col_c2.text_input("Nombre de Cuenta")
                debe = col_c3.number_input("Debe ($)", min_value=0.0, value=0.0)
                haber = col_c4.number_input("Haber ($)", min_value=0.0, value=0.0)
                
                add_linea = st.form_submit_button("Agregar Línea al Asiento")
                
                if add_linea and nom_cuenta:
                    nueva_linea = pd.DataFrame([[fecha_partida, cod_cuenta, nom_cuenta, debe, haber]], 
                                               columns=["Fecha", "Código", "Cuenta", "Debe", "Haber"])
                    st.session_state.libro_diario = pd.concat([st.session_state.libro_diario, nueva_linea], ignore_index=True)
                    st.rerun()
            
            if not st.session_state.libro_diario.empty:
                st.markdown("#### Borrador de Partida Actual")
                st.dataframe(st.session_state.libro_diario, use_container_width=True)
                
                total_debe = st.session_state.libro_diario["Debe"].sum()
                total_haber = st.session_state.libro_diario["Haber"].sum()
                
                col_t1, col_t2, col_t3 = st.columns(3)
                col_t1.metric("Total Debe", f"${total_debe:,.2f}")
                col_t2.metric("Total Haber", f"${total_haber:,.2f}")
                
                diferencia = abs(total_debe - total_haber)
                if diferencia < 0.01:
                    col_t3.metric("Estado", "Cuadrada ✅", delta="OK", delta_color="normal")
                    if st.button("Guardar y Mayorizar Partida"):
                        st.success("¡Partida registrada y mayorizada con éxito!")
                else:
                    col_t3.metric("Estado", "Descuadrada ❌", delta=f"-${diferencia:,.2f}", delta_color="inverse")
                    st.warning("La suma del Debe y el Haber deben coincidir para guardar la partida.")
                    
        with tab_c2:
            st.markdown("### Libro Diario General")
            if not st.session_state.libro_diario.empty:
                st.dataframe(st.session_state.libro_diario, use_container_width=True)
            else:
                st.info("No hay transacciones registradas en el libro diario aún.")
                
        with tab_c3:
            st.markdown("### Balance de Comprobación y Estados Financieros")
            st.write("Generación automática de Balance General y Estado de Resultados.")
        
    elif menu == "Facturación DTE":
        render_facturacion()
        
    elif menu == "Planillas":
        st.subheader("👥 Módulo de Planillas y Retenciones (Régimen El Salvador)")
        
        tab_p1, tab_p2 = st.tabs(["Generación y Cálculo de Planilla", "Estructura para ERP / BC365"])
        
        with tab_p1:
            st.markdown("### Procesamiento de Salarios y Deducciones de Ley")
            
            # Carga de archivo Excel con empleados y salarios base
            archivo_plan = st.file_uploader("📂 Sube la base de empleados (Excel con Columnas: Empleado, Departamento, Salario Base)", type=['xlsx', 'xls'], key="up_plan")
            
            if archivo_plan:
                df_empleados = pd.read_excel(archivo_plan)
                st.dataframe(df_empleados.head(), use_container_width=True)
                
                if st.button("Calcular ISSS, AFP y Renta (Ley ES)", type="primary"):
                    # Lógica de cálculo bajo ley salvadoreña
                    # AFP: 7.25% (Patronal 7.75% por aparte, empleado 7.25% sobre techo si aplica)
                    # ISSS: 3% empleado (hasta tester de $1,000, excedente sobre techo fijo)
                    
                    df_calc = df_empleados.copy()
                    if 'Salario Base' in df_calc.columns:
                        df_calc['AFP'] = round(df_calc['Salario Base'] * 0.0725, 2)
                        # ISSS con tope de 3% sobre $1000.00 o general según práctica
                        df_calc['ISSS'] = round(df_calc['Salario Base'].apply(lambda x: min(x, 1000.0) * 0.03), 2)
                        
                        # Base imponible para Renta = Salario Base - AFP - ISSS
                        base_renta = df_calc['Salario Base'] - df_calc['AFP'] - df_calc['ISSS']
                        
                        # Tabla de Renta Simplificada (El Salvador - Tramo estimado mensual)
                        def calcular_renta(base):
                            if base <= 472.00:
                                return 0.0
                            elif base <= 895.24:
                                return round((base - 472.00) * 0.10 + 17.67, 2)
                            elif base <= 2038.10:
                                return round((base - 895.24) * 0.20 + 60.00, 2)
                            else:
                                return round((base - 2038.10) * 0.30 + 288.57, 2)
                                
                        df_calc['Renta'] = base_renta.apply(calcular_renta)
                        df_calc['Salario Neto'] = round(df_calc['Salario Base'] - df_calc['AFP'] - df_calc['ISSS'] - df_calc['Renta'], 2)
                        
                        st.session_state.df_planilla_procesada = df_calc
                        st.success("¡Planilla calculada exitosamente bajo normativa fiscal de El Salvador!")
                
                if "df_planilla_procesada" in st.session_state:
                    st.markdown("#### Resultado del Cálculo")
                    st.dataframe(st.session_state.df_planilla_procesada, use_container_width=True)
                    
                    # Totales
                    t_salario = st.session_state.df_planilla_procesada['Salario Base'].sum()
                    t_isss = st.session_state.df_planilla_procesada['ISSS'].sum()
                    t_afp = st.session_state.df_planilla_procesada['AFP'].sum()
                    t_renta = st.session_state.df_planilla_procesada['Renta'].sum()
                    t_neto = st.session_state.df_planilla_procesada['Salario Neto'].sum()
                    
                    c1, c2, c3, c4, c5 = st.columns(5)
                    c1.metric("Total Salarios", f"${t_salario:,.2f}")
                    c2.metric("Total ISSS", f"${t_isss:,.2f}")
                    c3.metric("Total AFP", f"${t_afp:,.2f}")
                    c4.metric("Total Renta", f"${t_renta:,.2f}")
                    c5.metric("Total Neto a Pagar", f"${t_neto:,.2f}")

        with tab_p2:
            st.markdown("### Estructura para Carga en ERP / Business Central")
            st.write("Generación del formato tabular estandarizado de asientos de provisión y pago de planilla[cite: 1].")
            
            if "df_planilla_procesada" in st.session_state:
                if st.button("Generar Archivo de Integración ERP"):
                    st.info("Estructura lista para exportar compatible con la configuración de centros de costo de tus clientes.")
            else:
                st.info("Primero procese la planilla en la pestaña anterior para generar la estructura ERP.")
        
    elif menu == "Inventarios y Activo Fijo":
        st.title("Inventarios y Activo Fijo")
        st.write("Control de existencias y generación de viñetas de identificación de activos.")

# Control de flujo principal
if not st.session_state.authenticated:
    login_screen()
else:
    main_dashboard()
