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

# Base de datos de perfiles de empresas por usuario/NIT
if "empresas_config" not in st.session_state:
    st.session_state.empresas_config = {
        "06140806831121": {
            "razon_social": "RI Consultores S.A. de C.V.",
            "nombre_comercial": "RI Consultores",
            "nit": "0614-080683-112-1",
            "nrc": "123456-7",
            "giro": "Servicios de Contabilidad y Auditoría",
            "direccion": "San Salvador, El Salvador",
            "telefono": "+503 2222-2222",
            "correo": "contacto@riconsultores.com",
            "web": "www.riconsultores.com",
            "token_mh": ""
        }
    }

if "inventario_db" not in st.session_state:
    st.session_state.inventario_db = pd.DataFrame([
        {
            "SKU": "PROD-001", 
            "Descripción": "Servicio de Consultoría Contable", 
            "Stock": 100.0, 
            "Costo ($)": 0.0, 
            "Precio Unidad ($)": 50.0, 
            "Precio Mayoreo ($)": 45.0, 
            "Precio Especial ($)": 40.0
        },
        {
            "SKU": "PROD-002", 
            "Descripción": "Software / Licencia ERP Cloud", 
            "Stock": 50.0, 
            "Costo ($)": 10.0, 
            "Precio Unidad ($)": 35.0, 
            "Precio Mayoreo ($)": 30.0, 
            "Precio Especial ($)": 25.0
        }
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
                    # Si el usuario es nuevo, inicializamos su perfil por defecto
                    if user not in st.session_state.empresas_config:
                        st.session_state.empresas_config[user] = {
                            "razon_social": f"Empresa de {user}",
                            "nombre_comercial": "Mi Negocio",
                            "nit": user,
                            "nrc": "000000-0",
                            "giro": "Comercio General",
                            "direccion": "El Salvador",
                            "telefono": "0000-0000",
                            "correo": "correo@empresa.com",
                            "web": "www.empresa.com",
                            "token_mh": ""
                        }
                    st.rerun()
                else:
                    st.error("Por favor, ingrese sus credenciales.")


def render_facturacion():
    st.subheader("🧾 Emisión y Control de Documentos Tributarios Electrónicos (DTE)")
    
    # Obtenemos la configuración de la empresa del usuario actual
    config_actual = st.session_state.empresas_config.get(st.session_state.username, {})
    
    tab1, tab2, tab3 = st.tabs(["Emisión de DTE", "Historial y Sello", "⚙️ Configuración de Empresa (Emisor)"])
    
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
        st.markdown("#### Selección de Ítems (Compatible con Scanner de Código de Barras)")
        
        if st.session_state.inventario_db.empty:
            st.warning("No hay productos en el inventario.")
        else:
            with st.form("form_item_inventario"):
                opciones_sku = st.session_state.inventario_db["SKU"] + " - " + st.session_state.inventario_db["Descripción"]
                prod_seleccionado = st.selectbox("Seleccionar Artículo o Escanear SKU", options=opciones_sku)
                
                tipo_precio_sel = st.selectbox("Tipo de Precio a Aplicar", ["Precio Unidad ($)", "Precio Mayoreo ($)", "Precio Especial ($)"])
                cant = st.number_input("Cantidad a Facturar", min_value=1.0, value=1.0)
                
                add_item = st.form_submit_button("Agregar al DTE")
                
                if add_item and prod_seleccionado:
                    sku_code = prod_seleccionado.split(" - ")[0]
                    row_prod = st.session_state.inventario_db[st.session_state.inventario_db["SKU"] == sku_code].iloc[0]
                    
                    stock_actual = row_prod["Stock"]
                    precio_v = row_prod[tipo_precio_sel]
                    desc_prod = f"{row_prod['Descripción']} ({tipo_precio_sel.split()[0]})"
                    
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
            
            col_acciones_dte1, col_acciones_dte2 = st.columns(2)
            
            with col_acciones_dte1:
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
                    
            with col_acciones_dte2:
                # Ticket Preliminar con los datos dinámicos configurados por el cliente
                if st.button("🖨️ Imprimir Ticket Preliminar"):
                    ticket_html = f"""
                    <div style="width: 300px; font-family: monospace; font-size: 11px; padding: 10px; border: 1px dashed #333;">
                        <h3 style="text-align: center; margin: 0;">{config_actual.get('nombre_comercial', 'EMPRESA')}</h3>
                        <p style="text-align: center; margin: 0;">{config_actual.get('razon_social', '')}</p>
                        <p style="text-align: center; margin: 0;">NIT: {config_actual.get('nit', '')} | NRC: {config_actual.get('nrc', '')}</p>
                        <p style="text-align: center; margin: 0;">{config_actual.get('direccion', '')}</p>
                        <p style="text-align: center; margin: 0;">Tel: {config_actual.get('telefono', '')} | Web: {config_actual.get('web', '')}</p>
                        <hr>
                        <p style="text-align: center; margin: 0; font-weight: bold;">TICKET PRELIMINAR DE VENTA</p>
                        <p><b>Cliente:</b> {cliente_nombre or 'Consumidor Final'}</p>
                        <p><b>Fecha:</b> {fecha_emision}</p>
                        <hr>
                    """
                    for _, row in st.session_state.items_dte.iterrows():
                        ticket_html += f"<div>{row['Cantidad']}x {row['Descripción']} - ${row['Ventas Gravadas']:,.2f}</div>"
                    ticket_html += f"""
                        <hr>
                        <h4 style="text-align: right; margin: 0;">TOTAL: ${total_pagar:,.2f}</h4>
                        <p style="text-align: center; margin-top: 10px; font-size: 9px;">Documento sin validez fiscal - RI ERP Cloud</p>
                    </div>
                    <script>window.print();</script>
                    """
                    st.components.v1.html(ticket_html, height=450)

    with tab2:
        st.markdown("### Historial de Documentos Emitidos")

    with tab3:
        st.markdown("### ⚙️ Configuración del Perfil de Empresa y Datos del Emisor")
        st.info("Estos datos aparecerán automáticamente en los encabezados de tus facturas, tickets y documentos tributarios.")
        
        with st.form("form_config_empresa"):
            c_e1, c_e2 = st.columns(2)
            rs = c_e1.text_input("Razón Social", value=config_actual.get("razon_social", ""))
            nc = c_e2.text_input("Nombre Comercial", value=config_actual.get("nombre_comercial", ""))
            
            c_e3, c_e4 = st.columns(2)
            nit_emp = c_e3.text_input("NIT de la Empresa", value=config_actual.get("nit", ""))
            nrc_emp = c_e4.text_input("NRC (Número de Registro)", value=config_actual.get("nrc", ""))
            
            giro_emp = st.text_input("Giro / Actividad Económica", value=config_actual.get("giro", ""))
            dir_emp = st.text_input("Dirección Fiscal", value=config_actual.get("direccion", ""))
            
            c_e5, c_e6, c_e7 = st.columns(3)
            tel_emp = c_e5.text_input("Teléfono de Contacto", value=config_actual.get("telefono", ""))
            mail_emp = c_e6.text_input("Correo Electrónico", value=config_actual.get("correo", ""))
            web_emp = c_e7.text_input("Sitio Web", value=config_actual.get("web", ""))
            
            token_mh = st.text_input("Token / API Key de Transmisión Ministerio de Hacienda", type="password", value=config_actual.get("token_mh", ""))
            
            guardar_conf = st.form_submit_button("Guardar Configuración de Empresa", type="primary")
            if guardar_conf:
                st.session_state.empresas_config[st.session_state.username] = {
                    "razon_social": rs,
                    "nombre_comercial": nc,
                    "nit": nit_emp,
                    "nrc": nrc_emp,
                    "giro": giro_emp,
                    "direccion": dir_emp,
                    "telefono": tel_emp,
                    "correo": mail_emp,
                    "web": web_emp,
                    "token_mh": token_mh
                }
                st.success("¡Datos de la empresa actualizados correctamente!")
                st.rerun()


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
    st.subheader("📦 Módulo de Inventarios Avanzado (Precios Múltiples y Carga Masiva)")
    
    columnas_requeridas = ["SKU", "Descripción", "Stock", "Costo ($)", "Precio Unidad ($)", "Precio Mayoreo ($)", "Precio Especial ($)"]
    for col in columnas_requeridas:
        if col not in st.session_state.inventario_db.columns:
            st.session_state.inventario_db[col] = 0.0 if "($)" in col or col == "Stock" else ""

    tab_i0, tab_i1, tab_i2 = st.tabs(["📥 Carga Masiva Inicial", "Control de Stock y Precios", "Registro de Compras (Entradas)"])
    
    with tab_i0:
        st.markdown("### Importación Masiva de Inventario (Excel / CSV)")
        st.info("Sube un archivo con las columnas: SKU, Descripción, Stock, Costo ($), Precio Unidad ($), Precio Mayoreo ($), Precio Especial ($).")
        
        archivo_carga = st.file_uploader("Selecciona archivo de inventario inicial", type=["csv", "xlsx"])
        if archivo_carga:
            try:
                if archivo_carga.name.endswith('.csv'):
                    df_upload = pd.read_csv(archivo_carga)
                else:
                    df_upload = pd.read_excel(archivo_carga)
                
                st.markdown("Vista previa de los datos a importar:")
                st.dataframe(df_upload.head(), use_container_width=True)
                
                if st.button("Confirmar e Importar al Inventario General", type="primary"):
                    for col in columnas_requeridas:
                        if col not in df_upload.columns and col != "SKU":
                            df_upload[col] = 0.0
                    st.session_state.inventario_db = pd.concat([st.session_state.inventario_db, df_upload[columnas_requeridas]], ignore_index=True)
                    st.success("¡Inventario cargado masivamente con éxito!")
                    st.rerun()
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

    with tab_i1:
        st.markdown("### Maestro de Artículos, Costos y Precios Múltiples")
        df_inv = st.session_state.inventario_db.copy()
        df_inv["Margen Unidad ($)"] = df_inv["Precio Unidad ($)"] - df_inv["Costo ($)"]
        df_inv["Margen (%)"] = ((df_inv["Margen Unidad ($)"] / df_inv["Precio Unidad ($)"]) * 100).fillna(0).round(2)
        st.dataframe(df_inv, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### Registro Individual o Edición de Producto")
        with st.form("form_nuevo_prod_avanzado"):
            c1, c2, c3 = st.columns(3)
            sku = c1.text_input("SKU / Código de Barras", value=f"PROD-00{len(df_inv)+1}")
            desc = c2.text_input("Descripción del Producto")
            stock_ini = c3.number_input("Stock Inicial", min_value=0.0, value=10.0)
            
            c4, c5, c6, c7 = st.columns(4)
            costo = c4.number_input("Costo Unitario ($)", min_value=0.0, value=5.0)
            precio_u = c5.number_input("Precio Unidad ($)", min_value=0.0, value=10.0)
            precio_m = c6.number_input("Precio Mayoreo ($)", min_value=0.0, value=8.50)
            precio_e = c7.number_input("Precio Especial ($)", min_value=0.0, value=7.50)
            
            guardar_prod = st.form_submit_button("Guardar Producto en Inventario")
            if guardar_prod and desc:
                nuevo = pd.DataFrame([{
                    "SKU": sku, 
                    "Descripción": desc, 
                    "Stock": stock_ini, 
                    "Costo ($)": costo, 
                    "Precio Unidad ($)": precio_u, 
                    "Precio Mayoreo ($)": precio_m, 
                    "Precio Especial ($)": precio_e
                }])
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
