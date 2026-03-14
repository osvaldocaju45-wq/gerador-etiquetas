import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import io

st.title("Gerador de Etiquetas 40×25 mm – Zebra ZD220")
st.write("Envie o PDF original da Shopee (60×40 mm). O app gera um PDF com duas etiquetas por página, no tamanho real 80×25 mm.")

uploaded_file = st.file_uploader("Envie o PDF original", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()

    # Abre o PDF com PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    imagens = []

    # Converte cada página em imagem com DPI alto
    for page in doc:
        pix = page.get_pixmap(dpi=300)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        imagens.append(img)

    # Tamanho real da etiqueta (40×25 mm)
    etiqueta_w_mm = 40
    etiqueta_h_mm = 25

    # Converte mm → pixels (300 DPI)
    etiqueta_w_px = int((etiqueta_w_mm / 25.4) * 300)
    etiqueta_h_px = int((etiqueta_h_mm / 25.4) * 300)

    # Redimensiona cada etiqueta
    resized = [img.resize((etiqueta_w_px, etiqueta_h_px), Image.LANCZOS) for img in imagens]

    # Página final: 80×25 mm (duas etiquetas lado a lado)
    page_w_mm = 80
    page_h_mm = 25

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(page_w_mm * mm, page_h_mm * mm))

    for i in range(0, len(resized), 2):
        img1 = resized[i]
        img2 = resized[i+1] if i+1 < len(resized) else resized[i]

        # Salva temporariamente as imagens
        img1_io = io.BytesIO()
        img1.save(img1_io, format="PNG")
        img1_io.seek(0)

        img2_io = io.BytesIO()
        img2.save(img2_io, format="PNG")
        img2_io.seek(0)

        # Desenha as duas etiquetas no PDF
        c.drawImage(img1_io, 0 * mm, 0 * mm, width=etiqueta_w_mm * mm, height=etiqueta_h_mm * mm)
        c.drawImage(img2_io, 40 * mm, 0 * mm, width=etiqueta_w_mm * mm, height=etiqueta_h_mm * mm)

        c.showPage()

    c.save()
    buffer.seek(0)

    st.download_button(
        label="Baixar PDF Final (80×25 mm, 2 etiquetas)",
        data=buffer,
        file_name="etiquetas_80x25mm.pdf",
        mime="application/pdf"
    )

    st.success("PDF gerado com tamanho real! Agora a Zebra imprime perfeito.")
