import os
import json
from datetime import datetime
import streamlit as st
from PIL import Image
from fpdf import FPDF

# Configuración de carpetas locales
DATA_DIR = "datos"
LOGOS_DIR = os.path.join(DATA_DIR, "logos")
DB_FILE = os.path.join(DATA_DIR, "clientes_logos.json")

os.makedirs(LOGOS_DIR, exist_ok=True)

def cargar_datos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_datos(datos):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

# Clase de diseño del PDF con formato técnico limpio
class FichaProduccionPDF(FPDF):
    def dibujar_ficha(self, data):
        self.add_page()
        self.set_auto_page_break(auto=False)
        self.set_margins(15, 12, 15)

        # 1. ENCABEZADO SUPERIOR
        # Logo / Marca Nova Seguridad
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(30, 41, 59)
        self.cell(70, 9, "NOVA", ln=1)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(100, 116, 139)
        self.cell(70, 5, "SEGURIDAD INDUSTRIAL", ln=0)

        # Título Central
        self.set_xy(80, 14)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(15, 23, 42)
        self.cell(60, 10, "ORDEN DE PRODUCCIÓN", border=0, align="C")

        # Recuadro Superior Derecho: Logo Cliente
        x_box_logo = 145
        y_box_logo = 12
        w_box_logo = 50
        h_box_logo = 26

        self.set_draw_color(180, 180, 180)
        self.rect(x_box_logo, y_box_logo, w_box_logo, h_box_logo)
        
        self.set_xy(x_box_logo, y_box_logo + 1)
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(120, 120, 120)
        self.cell(w_box_logo, 4, "LOGO CLIENTE", align="C", ln=1)

        # Incrustar imagen en el recuadro superior si existe
        if data.get("logo_path") and os.path.exists(data["logo_path"]):
            try:
                self.image(data["logo_path"], x=x_box_logo + 5, y=y_box_logo + 5, w=w_box_logo - 10, h=h_box_logo - 7)
            except Exception:
                pass

        # Línea separadora
        self.set_draw_color(200, 200, 200)
        self.line(15, 42, 195, 42)

        # 2. DATOS GENERALES (Bloque ordenado)
        self.set_xy(15, 46)
        
        # Fila 1: Cliente y Fecha
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(50, 50, 50)
        self.cell(32, 6, "CLIENTE:", border=0)
        self.set_font("Helvetica", "", 9)
        self.cell(75, 6, str(data["cliente"]), border="B")
        
        self.cell(8, 6, "") # Espacio
        self.set_font("Helvetica", "B", 9)
        self.cell(20, 6, "FECHA:", border=0)
        self.set_font("Helvetica", "", 9)
        self.cell(45, 6, str(data["fecha"]), border="B", ln=1)

        # Fila 2: Nota de Venta y Nombre Logo
        self.ln(2)
        self.set_font("Helvetica", "B", 9)
        self.cell(32, 6, "NOTA DE VENTA:", border=0)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(15, 23, 42)
        self.cell(75, 6, str(data["nota_venta"]), border="B")

        self.cell(8, 6, "")
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(50, 50, 50)
        self.cell(28, 6, "VARIANTE LOGO:", border=0)
        self.set_font("Helvetica", "", 9)
        self.cell(37, 6, str(data["nombre_logo"]), border="B", ln=1)

        self.ln(6)

        # 3. SECCIÓN: TÉCNICA Y POSICIONES
        self.set_fill_color(241, 245, 249)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(15, 23, 42)
        self.cell(180, 7, f" ESPECIFICACIÓN TÉCNICA: {data['tipo_trabajo'].upper()}", border=1, fill=True, ln=1)

        # Tabla de casillas de ubicación
        posiciones = ["PECHO DERECHO", "PECHO IZQUIERDO", "ESPALDA", "BOLSILLO TAPETA", "OTRO"]
        ancho_col = 180 / len(posiciones)

        self.set_font("Helvetica", "B", 8)
        self.set_text_color(70, 70, 70)
        for pos in posiciones:
            self.cell(ancho_col, 6, pos, border=1, align="C")
        self.ln()

        self.set_font("Helvetica", "B", 11)
        self.set_text_color(220, 38, 38) # Marca en rojo visual nítido
        for pos in posiciones:
            marca = "X" if pos == data["posicion_seleccionada"] else ""
            self.cell(ancho_col, 7, marca, border=1, align="C")
        self.ln(8)

        # 4. TABLA DE DETALLES TÉCNICOS
        self.set_text_color(50, 50, 50)
        
        self.set_font("Helvetica", "B", 8)
        self.cell(45, 6, "COLOR(ES) HILOS / TINTAS:", border=0)
        self.set_font("Helvetica", "", 9)
        self.cell(135, 6, str(data["colores"]), border="B", ln=1)
        self.ln(2)

        self.set_font("Helvetica", "B", 8)
        self.cell(45, 6, "DIMENSIONES:", border=0)
        self.set_font("Helvetica", "", 9)
        self.cell(135, 6, str(data["tamano"]), border="B", ln=1)
        self.ln(2)

        self.set_font("Helvetica", "B", 8)
        self.cell(45, 6, "OBSERVACIONES / PRENDA:", border=0)
        self.set_font("Helvetica", "", 9)
        self.cell(135, 6, str(data["observaciones"]), border="B", ln=1)

        # 5. RECUADRO INFERIOR DE DETALLE TALLER
        self.ln(8)
        y_visual = self.get_y()
        self.set_draw_color(200, 200, 200)
        self.set_fill_color(250, 250, 250)
        self.rect(15, y_visual, 180, 115, style="DF")

        self.set_xy(18, y_visual + 3)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(100, 116, 139)
        self.cell(174, 5, f"VISTA PREVIA DEL TRABAJO A REALIZAR EN TALLER ({data['posicion_seleccionada']})", align="C", ln=1)

        # Montaje central del logo grande para guía visual del operador
        if data.get("logo_path") and os.path.exists(data["logo_path"]):
            try:
                self.image(data["logo_path"], x=65, y=y_visual + 25, w=80)
            except Exception:
                pass


# INTERFAZ STREAMLIT
st.set_page_config(page_title="Nova Seguridad - Órdenes", layout="wide", page_icon="🦺")
st.title("🦺 Generador de Órdenes de Producción")

db = cargar_datos()

pestana1, pestana2 = st.tabs(["📋 Generar Orden de Taller", "🏢 Catálogo de Clientes y Logos"])

with pestana1:
    if not db:
        st.info("👋 Aún no hay clientes registrados. Pasa a la pestaña 'Catálogo de Clientes y Logos' para dar de alta el primero.")
    else:
        col_form, col_preview = st.columns([1.1, 0.9])

        with col_form:
            st.subheader("1. Selección de Cliente y Logo")
            cliente_sel = st.selectbox("Cliente", options=sorted(list(db.keys())))
            logos_cliente = db[cliente_sel].get("logos", {})

            if not logos_cliente:
                st.warning("Este cliente aún no tiene variantes de logos cargadas.")
            else:
                nombre_logo_sel = st.selectbox("Variante de Logo", options=list(logos_cliente.keys()))
                datos_logo = logos_cliente[nombre_logo_sel]

                st.subheader("2. Datos de la Orden")
                col_nv, col_tipo = st.columns(2)
                with col_nv:
                    nota_venta = st.text_input("Nota de Venta", placeholder="Ej: 6005597")
                with col_tipo:
                    tipo_trabajo = st.selectbox("Técnica", ["Bordado", "Estampado / Transfer"])

                posicion = st.selectbox(
                    "Ubicación en la prenda",
                    ["PECHO IZQUIERDO", "PECHO DERECHO", "ESPALDA", "BOLSILLO TAPETA", "OTRO"]
                )

                colores = st.text_input("Colores sugeridos", value=datos_logo.get("colores_defecto", ""))
                tamano = st.text_input("Dimensiones", value=datos_logo.get("tamano_defecto", ""))
                observaciones = st.text_input("Detalle de la prenda", value="Chalecos geólogos naranjos con reflectante")

        with col_preview:
            if logos_cliente and nombre_logo_sel:
                st.subheader("Vista Previa")
                ruta_logo = datos_logo.get("ruta_archivo", "")
                if os.path.exists(ruta_logo):
                    st.image(ruta_logo, caption=f"Logo activo: {nombre_logo_sel}", width=220)

                st.markdown("---")
                if st.button("📄 Generar y Descargar Orden PDF", type="primary", use_container_width=True):
                    if not nota_venta:
                        st.error("Debes ingresar la Nota de Venta antes de generar la orden.")
                    else:
                        datos_orden = {
                            "cliente": cliente_sel,
                            "fecha": datetime.now().strftime("%d-%m-%Y"),
                            "nota_venta": nota_venta,
                            "nombre_logo": nombre_logo_sel,
                            "tipo_trabajo": tipo_trabajo,
                            "posicion_seleccionada": posicion,
                            "colores": colores,
                            "tamano": tamano,
                            "observaciones": observaciones,
                            "logo_path": ruta_logo
                        }

                        pdf = FichaProduccionPDF()
                        pdf.dibujar_ficha(datos_orden)
                        nombre_pdf = f"Orden_{nota_venta}_{cliente_sel}.pdf"
                        pdf.output(nombre_pdf)

                        with open(nombre_pdf, "rb") as f:
                            st.download_button(
                                label="⬇️ Descargar Ficha PDF Lista",
                                data=f,
                                file_name=nombre_pdf,
                                mime="application/pdf",
                                use_container_width=True
                            )

with pestana2:
    st.subheader("Registro de Clientes y Logos Múltiples")
    modo = st.radio("¿Qué deseas hacer?", ["Registrar Nuevo Cliente", "Agregar Logo a Cliente Existente"], horizontal=True)

    if modo == "Registrar Nuevo Cliente":
        nombre_cliente = st.text_input("Nombre de la Empresa / Cliente (ej: Transcar Spa)")
    else:
        if db:
            nombre_cliente = st.selectbox("Selecciona la Empresa", options=sorted(list(db.keys())))
        else:
            nombre_cliente = st.text_input("Nombre de la Empresa")

    col_1, col_2 = st.columns(2)
    with col_1:
        variante = st.text_input("Nombre de esta variante (ej: Pecho Principal, Espalda Grande, Monocromo)")
        colores_def = st.text_input("Colores habituales (ej: AZUL - NARANJO)")
    with col_2:
        medida_def = st.text_input("Medidas habituales (ej: 10,5 cm x 6 cm)")
        archivo_logo = st.file_uploader("Subir imagen del logo (PNG o JPG)", type=["png", "jpg", "jpeg"])

    if st.button("💾 Guardar en el Catálogo", use_container_width=True):
        if not nombre_cliente or not variante or not archivo_logo:
            st.error("Por favor completa el nombre de cliente, la variante y sube la imagen.")
        else:
            ext = archivo_logo.name.split(".")[-1]
            archivo_guardado = f"{nombre_cliente.strip().replace(' ', '_')}_{variante.strip().replace(' ', '_')}.{ext}"
            ruta_final = os.path.join(LOGOS_DIR, archivo_guardado)

            with open(ruta_final, "wb") as f:
                f.write(archivo_logo.get_buffer())

            if nombre_cliente not in db:
                db[nombre_cliente] = {"logos": {}}

            db[nombre_cliente]["logos"][variante] = {
                "ruta_archivo": ruta_final,
                "colores_defecto": colores_def,
                "tamano_defecto": medida_def
            }

            guardar_datos(db)
            st.success(f"¡Logo '{variante}' guardado exitosamente para {nombre_cliente}!")
            st.rerun()
