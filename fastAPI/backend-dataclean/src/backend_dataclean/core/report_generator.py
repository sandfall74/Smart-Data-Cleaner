import io
import json
import pandas as pd
from fpdf import FPDF
from backend_dataclean.schemas.clean import CleanResponse


def export_dataframe_to_bytes(df: pd.DataFrame, format_type: str = "csv") -> tuple[bytes, str, str]:
    """
    Exporta un DataFrame a bytes en formato CSV o Excel.
    Retorna: (bytes_content, media_type, file_extension)
    """
    fmt = format_type.lower().strip()

    if fmt in ("xlsx", "excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Datos_Limpios")
        return (
            output.getvalue(),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "xlsx",
        )

    # Por defecto CSV 
    csv_string = df.to_csv(index=False, encoding="utf-8-sig")
    return csv_string.encode("utf-8-sig"), "text/csv", "csv"

class AuditPDF(FPDF):
    """estructura base del PDF de auditoría."""

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(30, 41, 59)  
        self.cell(0, 10, "Reporte de Limpieza y Auditoría de Datos", border=False, new_x="LMARGIN", new_y="NEXT", align="L")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, "Smart Data Cleaner - Informe Autogenerado", border=False, new_x="LMARGIN", new_y="NEXT", align="L")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")

def generate_audit_pdf_bytes(response: CleanResponse) -> bytes:
    """construye un documento PDF """
    pdf = AuditPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # --- resumen Ejecutivo ---
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "1. Resumen General", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(51, 65, 85)

    # metricas principales
    pdf.cell(95, 6, f"Filas iniciales: {response.rows_before}")
    pdf.cell(95, 6, f"Filas finales: {response.rows_after}", new_x="LMARGIN", new_y="NEXT")

    pdf.cell(95, 6, f"Columnas iniciales: {response.columns_before}")
    pdf.cell(95, 6, f"Columnas finales: {response.columns_after}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(16, 185, 129)  # Verde Esmeralda
    pdf.cell(0, 8, f"Nuevo Health Score: {response.new_health_score} / 100", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(5)

    # --- bitacora de Cambios ---
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "2. Bitácora de Transformaciones", new_x="LMARGIN", new_y="NEXT")

    if not response.audit_log:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 6, "No se registraron cambios en el conjunto de datos.", new_x="LMARGIN", new_y="NEXT")
    else:
        # encabezado de la tabla
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(241, 245, 249)
        pdf.set_text_color(51, 65, 85)

        pdf.cell(20, 7, "Hora", border=1, fill=True)
        pdf.cell(45, 7, "Operación", border=1, fill=True)
        pdf.cell(100, 7, "Detalle", border=1, fill=True)
        pdf.cell(25, 7, "Filas (+/-)", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        # celdas de contenido
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(30, 41, 59)

        for entry in response.audit_log:
            # manejo básico de caracteres para FPDF
            operacion = entry.operacion.encode("latin-1", "replace").decode("latin-1")
            detalle = entry.detalle.encode("latin-1", "replace").decode("latin-1")
            delta = f"{entry.delta_filas:+d}" if entry.delta_filas != 0 else "="

            pdf.cell(20, 6, entry.momento, border=1)
            pdf.cell(45, 6, operacion[:25], border=1)
            pdf.cell(100, 6, detalle[:65], border=1)
            pdf.cell(25, 6, delta, border=1, new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())


def generate_audit_summary_json(response: CleanResponse) -> bytes:
    """genera un archivo JSON descargable con el resumen de auditoría y métricas."""
    data = response.model_dump()
    json_bytes = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
    return json_bytes