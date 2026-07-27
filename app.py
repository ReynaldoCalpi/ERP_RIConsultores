import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(
    page_title="RI ERP Cloud",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

if "inventario_db" not in st.session_state:
    st.session_state.inventario_db = pd.DataFrame([
        {"SKU": "PROD-001", "Descripción": "Servicio de Consultoría Contable", "Stock": 100.0, "Costo ($)": 0.0, "Precio Venta ($)": 50.0},
        {"SKU": "PROD-002", "Descripción": "Software / Licencia ERP Cloud", "Stock": 50.0, "Costo ($)": 10.0, "Precio Venta ($)": 35.0}
    ])

if "items_dte" not in st.session_state:
    st.session_state.items_dte = pd.DataFrame(columns=["SKU", "Cantidad", "Descripción", "Precio Unitario", "Ventas Gravadas"])

if "libro_diario" not in st.session_state:
    st.session_state.libro_diario = pd.DataFrame(columns=["Fecha", "Código", "Cuenta", "Debe", "Haber"])


def login_screen():
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
    st.subheader("🧾 Emisión y Control de Documentos Tributarios Electrónicos (DTE)")
    
    tab1, tab2, tab3 = st.tabs(["Emisión de DTE", "Historial y Sello", "Configuración Emisor"])
    
    with tab1:
        st.markdown("### Generar Nuevo Documento (Descuenta Stock Automáticamente)")
        
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
        st.markdown("#### Selección de Ítems desde el Inventario")
        
        if st.session_state.inventario_db.empty:
            st.warning("No hay productos en el inventario.")
        else:
            with st.form("form_item_inventario"):
                opciones_sku = st.session_state.inventario_db["SKU"] + " - " + st.session_state.inventario_db["Descripción"]
                prod_seleccionado = st.selectbox("Seleccionar Artículo", options=opciones_sku)
                cant = st.number_input("Cantidad a Facturar", min_value=1.0, value=1.0)
                
                add_item = st.form_submit_button("Agregar al DTE")
                
                if add_item and prod_seleccionado:
                    sku_code = prod_seleccionado.split(" - ")[0]
                    row_prod = st.session_state.inventario_db[st.session_state.inventario_db["SKU"] == sku_code].iloc[0]
                    
                    stock_actual = row_prod["Stock"]
                    precio_v = row_prod["Precio Venta ($)"]
                    desc_prod = row_prod["Descripción"]
                    
                    if cant > stock_actual:
                        st.error(f"Stock insuficiente. Disponible: {stock_actual}")
                    else:
                        subtotal = cant * precio_v
                        nuevo_row = pd.DataFrame([[sku_code, cant, desc_prod, precio_v, subtotal]], 
                                                   columns=["SKU", "Cantidad", "Descripción", "Precio Unitario", "Ventas Gravadas"])
                        st.session_state.items_dte = pd.concat([st.session_state.items_dte, nuevo_row], ignore_index=True)
                        st.rerun()
                
        if not st.session_state.items_dte.empty:
            st.markdown("#### Detalle del Documento")
            st.dataframe(st.session_state.items_dte, use_container_width=True)
            
            total_gravado = st.session_state.items_dte["Ventas Gravadas"].sum()
            iva = total_gravado * 0.13 if "CCF" in tipo_dte else 0.0 
            total_pagar = total_gravado + iva if "CCF" in tipo_dte else total_gravado
            
            st.markdown(f"**Subtotal Gravado:** ${total_gravado:,.2f}")
            if "CCF" in tipo_dte:
                st.markdown(f"**IVA (13%):** ${iva:,.2f}")
            st.markdown(f"### **Total a Pagar: ${total_pagar:,.2f}**")
            
            if st.button("Transmitir DTE y Descargar Inventario"):
                for _, item in st.session_state.items_dte.iterrows():
                    sku_i = item["SKU"]
                    cant_i = item["Cantidad"]
                    idx = st.session_state.inventario_db[st.session_state.inventario_db["SKU"] == sku_i].index[0]
                    st.session_state.inventario_db.loc[idx, "Stock"] -= cant_i
                
                st.session_state.items_dte = pd.DataFrame(columns=["SKU", "Cantidad", "Descripción", "Precio Unitario", "Ventas Gravadas"])
                st.success("¡DTE transmitido y stock actualizado!")
                st.balloons()
                st.rerun()

    with tab2:
        st.markdown("### Historial de Documentos Emitidos")
    with tab3:
        st.markdown("### Parámetros de Transmisión")
        st.text_input("API Key / Token MH", type="password")


def render_contabilidad():
    st.subheader("📊 Módulo de Contabilidad y Partida Doble")
    tab_c1, tab_c2, tab_c3 = st.tabs(["Registro de Partidas", "Libro Diario", "Estados Financieros"])
    
    with tab_c1:
        st.markdown("### Nueva Partida Contable")
        fecha_partida = st.date_input("Fecha de Operación", datetime.now(), key="fecha_p")
        concepto = st.text_input("Concepto General de la Partida")
        
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
            st.dataframe(st.session_state.libro_diario, use_container_width=True)
            total_debe = st.session_state.libro_diario["Debe"].sum()
            total_haber = st.session_state.libro_diario["Haber"].sum()
            
            col_t1, col_t2, col_t3 = st.columns(3)
            col_t1.metric("Total Debe", f"${total_debe:,.2f}")
            col_t2.metric("Total Haber", f"${total_haber:,.2f}")
            
            diferencia = abs(total_debe - total_haber)
            if diferencia < 0.01:
                col_t3.metric("Estado", "Cuadrada ✅")
                if st.button("Guardar y Mayorizar Partida"):
                    st.success("¡Partida registrada con éxito!")
            else:
                col_t3.metric("Estado", "Descuadrada ❌", delta=f"-${diferencia:,.2f}")
                st.warning("Debe y Haber deben coincidir.")

    with tab_c2:
        st.markdown("### Libro Diario General")
        if not st.session_state.libro_diario.empty:
            st.dataframe(st.session_state.libro_diario, use_container_width=True)
    with tab_c3:
        st.markdown("### Estados Financieros")


def render_planillas():
    st.subheader("👥 Módulo de Planillas y Retenciones (Régimen El Salvador)")
    tab_p1, tab_p2 = st.tabs(["Generación y Cálculo de Planilla", "Estructura para ERP"])
    
    with tab_p1:
        archivo_plan = st.file_uploader("📂 Sube la base de empleados", type=['xlsx', 'xls'], key="up_plan")
        if archivo_plan:
            df_empleados = pd.read_excel(archivo_plan)
            st.dataframe(df_empleados.head(), use_container_width=True)
            
            if st.button("Calcular ISSS, AFP y Renta (Ley ES)", type="primary"):
                df_calc = df_empleados.copy()
                if 'Salario Base' in df_calc.columns:
                    df_calc['AFP'] = round(df_calc['Salario Base'] * 0.0725, 2)
                    df_calc['ISSS'] = round(df_calc['Salario Base'].apply(lambda x: min(x, 1000.0) * 0.03), 2)
                    base_renta = df_calc['Salario Base'] - df_calc['AFP'] - df_calc['ISSS']
                    
                    def calcular_renta(base):
                        if base <= 472.00: return 0.0
                        elif base <= 895.24: return round((base - 472.00) * 0.10 + 17.67, 2)
                        elif base <= 2038.10: return round((base - 895.24) * 0.20 + 60.00, 2)
                        else: return round((base - 2038.10) * 0.30 + 288.57, 2)
                            
                    df_calc['Renta'] = base_renta.apply(calcular_renta)
                    df_calc['Salario Neto'] = round(df_calc['Salario Base'] - df_calc['AFP'] - df_calc['ISSS'] - df_calc['Renta'], 2)
                    st.session_state.df_planilla_procesada = df_calc
                    st.success("¡Planilla calculada exitosamente!")
            
            if "df_planilla_procesada" in st.session_state:
                st.dataframe(st.session_state.df_planilla_procesada, use_container_width=True)

    with tab_p2:
        st.markdown("### Estructura para Carga en ERP")


def render_inventarios():
    st.subheader("📦 Módulo de Inventarios y Análisis de Márgenes")
    
    columnas_requeridas = ["SKU", "Descripción", "Stock", "Costo ($)", "Precio Venta ($)"]
    for col in columnas_requeridas:
        if col not in st.session_state.inventario_db.columns:
            st.session_state.inventario_db[col] = 0.0 if "($)" in col or col == "Stock" else ""

    tab_i1, tab_i2 = st.tabs(["Control de Stock y Márgenes", "Registro de Compras (Entradas)"])
    
    with tab_i1:
        st.markdown("### Maestro de Artículos, Costos y Precios de Venta")
        df_inv = st.session_state.inventario_db.copy()
        df_inv["Margen Bruto ($)"] = df_inv["Precio Venta ($)"] - df_inv["Costo ($)"]
        df_inv["Margen (%)"] = ((df_inv["Margen Bruto ($)"] / df_inv["Precio Venta ($)"]) * 100).fillna(0).round(2)
        st.dataframe(df_inv, use_container_width=True)
        
        st.markdown("---")
        with st.form("form_nuevo_prod_seguro"):
            c1, c2, c3, c4, c5 = st.columns(5)
            sku = c1.text_input("SKU", value=f"PROD-00{len(df_inv)+1}")
            desc = c2.text_input("Descripción")
            stock_ini = c3.number_input("Stock Inicial", min_value=0.0, value=10.0)
            costo = c4.number_input("Costo Unitario ($)", min_value=0.0, value=5.0)
            precio = c5.number_input("Precio Venta ($)", min_value=0.0, value=10.0)
            
            guardar_prod = st.form_submit_button("Guardar en Inventario")
            if guardar_prod and desc:
                nuevo = pd.DataFrame([{"SKU": sku, "Descripción": desc, "Stock": stock_ini, "Costo ($)": costo, "Precio Venta ($)": precio}])
                st.session_state.inventario_db = pd.concat([st.session_state.inventario_db, nuevo], ignore_index=True)
                st.success("¡Artículo registrado con éxito!")
                st.rerun()

    with tab_i2:
        st.markdown("### Registro de Entradas por Compras a Proveedores")
        if not st.session_state.inventario_db.empty:
            with st.form("form_compra_inv_seguro"):
                sku_compra = st.selectbox("Seleccionar Producto", options=st.session_state.inventario_db["SKU"] + " - " + st.session_state.inventario_db["Descripción"])
                cant_compra = st.number_input("Cantidad Comprada", min_value=1.0, value=10.0)
                nuevo_costo = st.number_input("Nuevo Costo Unitario de Compra ($)", min_value=0.0, value=5.0)
                
                procesar_compra = st.form_submit_button("Registrar Entrada al Inventario")
                if procesar_compra:
                    sku_code = sku_compra.split(" - ")[0]
                    idx = st.session_state.inventario_db[st.session_state.inventario_db["SKU"] == sku_code].index[0]
                    st.session_state.inventario_db.loc[idx, "Stock"] += cant_compra
                    st.session_state.inventario_db.loc[idx, "Costo ($)"] = nuevo_costo
                    st.success("¡Entrada registrada con éxito!")
                    st.rerun()


def main_dashboard():
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
        
    if menu == "Inicio":
        st.title("Panel de Control General")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Artículos en Inventario", len(st.session_state.inventario_db))
        col2.metric("IVA por Pagar", "$0.00")
        col3.metric("Planilla Activa", "$0.00")
        col4.metric("Estado del Sistema", "Óptimo 🚀")
    elif menu == "Contabilidad":
        render_contabilidad()
    elif menu == "Facturación DTE":
        render_facturacion()
    elif menu == "Planillas":
        render_planillas()
    elif menu == "Inventarios y Activo Fijo":
        render_inventarios()


if not st.session_state.authenticated:
    login_screen()
else:
    main_dashboard()
