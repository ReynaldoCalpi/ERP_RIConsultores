# Asegurar inicialización correcta del inventario con las columnas exactas
if "inventario_db" not in st.session_state:
    st.session_state.inventario_db = pd.DataFrame([
        {"SKU": "PROD-001", "Descripción": "Servicio de Consultoría Contable", "Stock": 100.0, "Costo ($)": 0.0, "Precio Venta ($)": 50.0},
        {"SKU": "PROD-002", "Descripción": "Software / Licencia ERP Cloud", "Stock": 50.0, "Costo ($)": 10.0, "Precio Venta ($)": 35.0}
    ])

def render_inventarios():
    """Módulo de Control de Existencias, Costos, Precios y Márgenes (Seguro y Aislado)"""
    st.subheader("📦 Módulo de Inventarios y Análisis de Márgenes")
    
    # Verificar y normalizar columnas si faltan por sesiones previas
    columnas_requeridas = ["SKU", "Descripción", "Stock", "Costo ($)", "Precio Venta ($)"]
    for col in columnas_requeridas:
        if col not in st.session_state.inventario_db.columns:
            if col == "Costo ($)":
                st.session_state.inventario_db[col] = 0.0
            elif col == "Precio Venta ($)":
                st.session_state.inventario_db[col] = 0.0
            else:
                st.session_state.inventario_db[col] = ""

    tab_i1, tab_i2 = st.tabs(["Control de Stock y Márgenes", "Registro de Compras (Entradas)"])
    
    with tab_i1:
        st.markdown("### Maestro de Artículos, Costos y Precios de Venta")
        
        df_inv = st.session_state.inventario_db.copy()
        df_inv["Margen Bruto ($)"] = df_inv["Precio Venta ($)"] - df_inv["Costo ($)"]
        df_inv["Margen (%)"] = ((df_inv["Margen Bruto ($)"] / df_inv["Precio Venta ($)"]) * 100).fillna(0).round(2)
        
        st.dataframe(df_inv, use_container_width=True)
        
        st.markdown("---")
        st.markdown("#### Registrar Nuevo Producto o Ajustar Precios")
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
        st.write("Las compras incrementan el stock y actualizan costos de adquisición.")
        
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
                    
                    st.success("¡Entrada registrada y stock incrementado correctamente!")
                    st.rerun()
