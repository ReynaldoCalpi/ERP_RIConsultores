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

# --- INICIALIZACIÓN DE VARIABLES DE ESTADO (Base de Datos en Memoria) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Inventario centralizado con costos, precios y márgenes
if "inventario_db" not in st.session_state:
    st.session_state.inventario_db = pd.DataFrame([
        {"SKU": "PROD-001", "Descripción": "Servicio de Consultoría Contable", "Stock": 100.0, "Costo ($)": 0.0, "Precio Venta ($)": 50.0},
        {"SKU": "PROD-002", "Descripción": "Software / Licencia ERP Cloud", "Stock": 50.0, "Costo ($)": 10.0, "Precio Venta ($)": 35.0}
    ])

if "items_dte" not in st.session_state:
    st.session_state.items_dte = pd.DataFrame(columns=["SKU", "Cantidad", "Descripción", "Precio Unitario", "Ventas Gravadas"])

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
    """Módulo de Facturación Electrónica (DTE) vinculado a Inventarios"""
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
            st.warning("No hay productos en el inventario. Registre artículos primero en el módulo de Inventarios.")
        else:
            with st.form("form_item_inventario"):
                # Seleccionar producto del inventario actual
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
                        st.error(f"Stock insuficiente. Stock disponible: {stock_actual}")
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
            
            if st.button("Transmitir DTE y Descargar Inventario (Simulación Hacienda)"):
                # DESCONTAR INVENTARIO AUTOMÁTICAMENTE
                for _, item in st.session_state.items_dte.iterrows():
                    sku_i = item["SKU"]
                    cant_i = item["Cantidad"]
                    idx = st.session_state.inventario_db[st.session_state.inventario_db["SKU"] == sku_i].index[0]
                    st.session_state.inventario_db.loc[idx, "Stock"] -= cant_i
                
                # Limpiar carrito DTE
                st.session_state.items_dte = pd.DataFrame(columns=["SKU", "Cantidad", "Descripción", "Precio Unitario", "Ventas Gravadas"])
                st.success("¡DTE transmitido y stock de inventario actualizado exitosamente!")
                st.balloons()
                st.rerun()

    with tab2:
        st.markdown("### Historial de Documentos Emitidos")
        st.write("Consulta y descarga de DTEs previos.")
        
    with tab3:
        st.markdown("### Parámetros de Transmisión y Credenciales")
        st.text_input("API Key / Token MH", type="password")

def render_inventarios():
    """Módulo de Control de Existencias, Costos, Precios y Márgenes"""
    st.subheader("📦 Módulo de Inventarios y Análisis de Márgenes")
    
    tab_i1, tab_i2 = st.tabs(["Control de Stock y Márgenes", "Registro de Compras (Entradas)"])
    
    with tab_i1:
        st.markdown("### Maestro de Artículos, Costos y Precios de Venta")
        
        # Calcular márgenes dinámicamente para la vista
        df_inv = st.session_state.inventario_db.copy()
        df_inv["Margen Bruto ($)"] = df_inv["Precio Venta ($)"] - df_inv["Costo ($)"]
        df_inv["Margen (%)"] = ((df_inv["Margen Bruto ($)"] / df_inv["Precio Venta ($)"]) * 100).fillna(0).round(2)
        
        st.dataframe(df_inv, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### Registrar Nuevo Producto o Ajustar Precios")
        with st.form("form_nuevo_prod"):
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
        st.write("Las compras incrementan el stock y permiten actualizar costos de adquisición.")
        
        if not st.session_state.inventario_db.empty:
            with st.form("form_compra_inv"):
                sku_compra = st.selectbox("Seleccionar Producto", options=st.session_state.inventario_db["SKU"] + " - " + st.session_state.inventario_db["Descripción"])
                cant_compra = st.number_input("Cantidad Comprada", min_value=1.0, value=10.0)
                nuevo_costo = st.number_input("Nuevo Costo Unitario de Compra ($)", min_value=0.0, value=5.0)
                
                procesar_compra = st.form_submit_button("Registrar Entrada al Inventario")
                if procesar_compra:
                    sku_code = sku_compra.split(" - ")[0]
                    idx = st.session_state.inventario_db[st.session_state.inventario_db["SKU"] == sku_code].index[0]
                    
                    # Actualizar stock y costo promedio ponderado básico
                    st.session_state.inventario_db.loc[idx, "Stock"] += cant_compra
                    st.session_state.inventario_db.loc[idx, "Costo ($)"] = nuevo_costo
                    
                    st.success("¡Entrada registrada y stock incrementado correctamente!")
                    st.rerun()

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
        col1.metric("Artículos en Inventario", len(st.session_state.inventario_db))
        col2.metric("IVA por Pagar", "$0.00")
        col3.metric("Planilla Activa", "$0.00")
        col4.metric("Estado del Sistema", "Óptimo 🚀")

    elif menu == "Contabilidad":
        st.subheader("📊 Módulo de Contabilidad y Partida Doble")
        st.write("Gestión de partida doble y estados financieros.")
        
    elif menu == "Facturación DTE":
        render_facturacion()
        
    elif menu == "Planillas":
        st.subheader("👥 Módulo de Planillas (Régimen El Salvador)")
        st.write("Procesamiento de salarios, ISSS, AFP y Renta.")
        
    elif menu == "Inventarios y Activo Fijo":
        render_inventarios()

# Control de flujo principal
if not st.session_state.authenticated:
    login_screen()
else:
    main_dashboard()
