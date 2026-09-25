import os
import json
from datetime import datetime
import streamlit as st
from PIL import Image
from fpdf import FPDF

# Configuración de carpetas
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

class FichaSegundaOpcionPDF(FPDF):
    def dibujar_tarjeta(self, x, y, w, h, titulo="", r=2):
        # Fondo blanco con borde suave
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(218, 224, 233)
        self.set_line_width(0.3)
        self.rect(x, y, w, h, style="DF")
        
        # Franja / Título si aplica
        if titulo:
            self.set_xy(x + 3, y + 2)
            self.set_font("Helvetica", "B", 7.5)
            self.set_text_color(15, 23, 42)
            self.cell(w - 6, 4, titulo.upper(), ln=1)
            self.set_draw_color(241, 245, 249)
            self.line(x + 2, y + 7, x + w - 2, y + 7)

    def generar(self, data):
        self.add_page()
        self.set_auto_page_break(auto=False)
        self.set_margins(10, 10, 10)

        # ----------------------------------------------------
        # 1. ENCABEZADO SUPERIOR OSCURO (Estilo Opción 2)
        # ----------------------------------------------------
        self.set_fill_color(11, 27, 44)  # Azul noche / casi negro
        self.rect(10, 10, 190, 22, style="F")

        # Texto Logo Nova Seguridad
        self.set_xy(14, 13)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(255, 255, 255)
        self.cell(60, 5, "NOVA SEGURIDAD", ln=1)
        self.set_xy(14, 19)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(148, 163, 184)
        self.cell(60, 4, "Soluciones en EPP y Vestuario", ln=0)

        # Línea vertical divisoria en el header
        self.set_draw_color(51, 65, 85)
        self.line(82, 13, 82, 29)

        # Título Central
        self.set_xy(86, 13)
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(255, 255, 255)
        self.cell(55, 5, "ORDEN TÉCNICA", ln=1)
        self.set_xy(86, 19)
        self.cell(55, 4, "DE PRODUCCIÓN", ln=0)

        # Caja derecha: NV y Fecha
        self.set_fill_color(22, 42, 66)
        self.rect(146, 12, 50, 18, style="F")
        self.set_xy(148, 14)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(248, 250, 252)
        self.cell(46, 4, f"N° NV: {data['nota_venta']}", ln=1, align="C")
        self.set_xy(148, 21)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(203, 213, 225)
        self.cell(46, 4, f"Fecha: {data['fecha']}", ln=0, align="C")

        # ----------------------------------------------------
        # 2. FILA 1: DATOS CLIENTE & FICHA TÉCNICA
        # ----------------------------------------------------
        y_fila1 = 35
        # Tarjeta 1: Datos Cliente
        self.dibujar_tarjeta(10, y_fila1, 92, 28, "1. DATOS DE CLIENTE")
        self.set_xy(14, y_fila1 + 9)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(100, 116, 139)
        self.cell(30, 4, "Empresa / Razón Social:", ln=1)
        self.set_x(14)
        self.set_font("Helvetica", "B", 8.5)
        self.set_text_color(15, 23, 42)
        self.cell(80, 5, str(data["cliente"]), ln=1)
        
        self.set_x(14)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(100, 116, 139)
        self.cell(30, 4, "Variante Logo:", ln=1)
        self.set_x(14)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(15, 23, 42)
        self.cell(80, 4, str(data["nombre_logo"]), ln=0)

        # Tarjeta 2: Ficha Técnica
        self.dibujar_tarjeta(106, y_fila1, 94, 28, "2. FICHA TÉCNICA")
        params = [
            ("Técnica:", str(data["tipo_trabajo"])),
            ("Colores Hilo:", str(data["colores"])),
            ("Dimensiones:", str(data["tamano"])),
            ("Tolerancia:", "± 2 mm")
        ]
        yp = y_fila1 + 8
        for label, val in params:
            self.set_xy(110, yp)
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(100, 116, 139)
            self.cell(24, 4, label)
            self.set_font("Helvetica", "B", 7.5)
            self.set_text_color(15, 23, 42)
            self.cell(64, 4, val)
            yp += 4.5

        # ----------------------------------------------------
        # 3. FILA 2: UBICACIÓN EN PRENDA
        # ----------------------------------------------------
        y_fila2 = 66
        self.dibujar_tarjeta(10, y_fila2, 190, 16, "3. UBICACIÓN EN PRENDA")
        
        posiciones = ["PECHO IZQUIERDO", "PECHO DERECHO", "ESPALDA", "BOLSILLO", "TAPETA", "OTRO"]
        x_pos = 14
        for pos in posiciones:
            # Cuadro checkbox
            marcado = (pos == data["posicion_seleccionada"])
            self.set_draw_color(100, 116, 139)
            self.rect(x_pos, y_fila2 + 9, 3.5, 3.5)
            if marcado:
                self.set_font("Helvetica", "B", 8)
                self.set_text_color(225, 29, 72)
                self.set_xy(x_pos, y_fila2 + 8.7)
                self.cell(3.5, 3.5, "X", align="C")
            
            self.set_xy(x_pos + 4.5, y_fila2 + 8.7)
            self.set_font("Helvetica", "B" if marcado else "", 7)
            self.set_text_color(15, 23, 42)
            self.cell(24, 4, pos.title())
            x_pos += 30

        # ----------------------------------------------------
        # 4. FILA 3: MONTAJE VISUAL Y MUESTRA LOGO
        # ----------------------------------------------------
        y_fila3 = 85
        # Bloque Prenda
        self.dibujar_tarjeta(10, y_fila3, 118, 90, "4. VISTA TÉCNICA PRENDA Y MONTAJE")
        self.set_xy(14, y_fila3 + 8)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(100, 116, 139)
        self.cell(50, 4, "VISTA FRONTAL", align="C")
        self.set_xy(70, y_fila3 + 8)
        self.cell(50, 4, "VISTA ESPALDA", align="C")

        # Texto pie de prenda
        self.set_xy(14, y_fila3 + 82)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(140, 140, 140)
        self.cell(110, 4, "Montaje referencial para taller según posición marcada", align="C")

        # Bloque Muestra Logo
        self.dibujar_tarjeta(132, y_fila3, 68, 90, "5. MUESTRA LOGO")
        if data.get("logo_path") and os.path.exists(data["logo_path"]):
            try:
                self.image(data["logo_path"], x=138, y=y_fila3 + 28, w=56)
            except Exception:
                pass

        # ----------------------------------------------------
        # 5. FILA 4: HILOS, TÉCNICA Y MEDIDAS (3 Cajas)
        # ----------------------------------------------------
        y_fila4 = 178
        # Caja 6: Colores Hilo
        self.dibujar_tarjeta(10, y_fila4, 58, 22, "6. COLORES HILO")
        self.set_xy(14, y_fila4 + 10)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(15, 23, 42)
        self.cell(50, 6, str(data["colores"]))

        # Caja 7: Técnica
        self.dibujar_tarjeta(72, y_fila4, 60, 22, "7. TÉCNICA / SERVICIO")
        self.set_xy(76, y_fila4 + 9)
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(15, 23, 42)
        self.cell(50, 4, f"[X] {data['tipo_trabajo']}")

        # Caja 8: Medidas
        self.dibujar_tarjeta(136, y_fila4, 64, 22, "8. MEDIDAS")
        self.set_xy(140, y_fila4 + 9)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(15, 23, 42)
        self.cell(55, 4, str(data["tamano"]))
        self.set_xy(140, y_fila4 + 14)
        self.set_font("Helvetica", "", 6.5)
        self.set_text_color(100, 116, 139)
        self.cell(55, 4, "Tolerancia técnica: ± 2 mm")

        # ----------------------------------------------------
        # 6. FILA 5: OBSERVACIONES
        # ----------------------------------------------------
        y_fila5 = 203
        self.dibujar_tarjeta(10, y_fila5, 190, 20, "9. OBSERVACIONES DE TALLER")
        self.set_xy(14, y_fila5 + 8)
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(30, 41, 59)
        self.multi_cell(182, 4, str(data["observaciones"]))

        # ----------------------------------------------------
        # 7. FILA 6: CONTROL Y FIRMAS
        # ----------------------------------------------------
        y_fila6 = 226
        self.dibujar_tarjeta(10, y_fila6, 60, 16, "Operador Taller")
        self.dibujar_tarjeta(74, y_fila6, 60, 16, "Control Calidad")
        self.set_xy(78, y_fila6 + 8)
        self.set_font("Helvetica", "", 7)
        self.cell(50, 4, "[ ] Aprobado    [ ] Rechazado")
        
        self.dibujar_tarjeta(138, y_fila6, 62, 16, "Fecha y Recepción")

        # ----------------------------------------------------
        # 8. PIE INFERIOR (Barra oscura y naranja)
        # ----------------------------------------------------
        self.set_fill_color(11, 27, 44)
        self.rect(10, 252, 190, 10, style="F")
        self.set_fill_color(249, 115, 22)  # Acento naranja
        self.rect(10, 250.5, 190, 1.5, style="F")

        self.set_xy(14, 254)
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(255, 255, 255)
        self.cell(100, 5, "NOVA SEGURIDAD  |  Departamento de Producción y Taller")
        self.set_xy(120, 254)
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(203, 213, 225)
        self.cell(76, 5, "Seguridad que nos mueve", align="R")


# INTERFAZ STREAMLIT
st.set_page_config(page_title="Nova Seguridad - Órdenes", layout="wide", page_icon="🦺")
st.title("🦺 Ficha Técnica de Producción Nova Seguridad")

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
                    ["PECHO IZQUIERDO", "PECHO DERECHO", "ESPALDA", "BOLSILLO", "TAPETA", "OTRO"]
                )

                colores = st.text_input("Colores sugeridos", value=datos_logo.get("colores_defecto", ""))
                tamano = st.text_input("Dimensiones", value=datos_logo.get("tamano_defecto", ""))
                observaciones = st.text_area(
                    "Observaciones de Taller", 
                    value="Prenda: Geólogos naranjos con cinta reflectante de 2\". Hilos resistentes al lavado industrial. Revisar centrado respecto al cierre frontal."
                )

        with col_preview:
            if logos_cliente and nombre_logo_sel:
                st.subheader("Vista Previa del Logo")
                ruta_logo = datos_logo.get("ruta_archivo", "")
                if os.path.exists(ruta_logo):
                    st.image(ruta_logo, caption=f"Logo activo: {nombre_logo_sel}", width=220)

                st.markdown("---")
                if st.button("📄 Generar Ficha Técnica PDF", type="primary", use_container_width=True):
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

                        pdf = FichaSegundaOpcionPDF()
                        pdf.generar(datos_orden)
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
        medida_def = st.text_input("Medidas habituales (ej: 10,5 cm x 6,0 cm)")
        archivo_logo = st.file_uploader("Subir imagen del logo (PNG o JPG)", type=["png", "jpg", "jpeg"])

    if st.button("💾 Guardar en el Catálogo", use_container_width=True):
        if not nombre_cliente or not variante or not archivo_logo:
            st.error("Por favor completa el nombre de cliente, la variante y sube la imagen.")
        else:
            ext = archivo_logo.name.split(".")[-1]
            archivo_guardado = f"{nombre_cliente.strip().replace(' ', '_')}_{variante.strip().replace(' ', '_')}.{ext}"
            ruta_final = os.path.join(LOGOS_DIR, archivo_guardado)

            with open(ruta_final, "wb") as f:
                f.write(archivo_logo.getbuffer())

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
