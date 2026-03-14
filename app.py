import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io

st.title("Gerador de Etiquetas 40×25 mm – Zebra ZD220")
st.write("Envie o PDF original da Shopee (60×40 mm). O app gera um PDF com duas etiquetas por página, reduzidas para 37,5×25 mm.")

uploaded_file = st.file_uploader("Envie o PDF original", type=["pdf"])

if uploaded_file:
    pdf_bytes = uploaded_file.read()

    # Abre o PDF com PyMuPDF
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    imagens = []

    # Converte cada página em imagem com DPI maior
    for page in doc:
        pix = page.get_pixmap(dpi=300)  # Aumenta nitidez
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        imagens.append(img)

    # Tamanho final da etiqueta (em pixels a 300 DPI)
    etiqueta_w = int(300 * 1.5)   # 37,5 mm
    etiqueta_h = int(300 * 1.0)   # 25 mm

    resized = [img.resize((etiqueta_w, etiqueta_h), Image.LANCZOS) for img in imagens]

    # Página final (80 mm × 25 mm → 300 DPI)
    page_w = int(300 * 3.0)   # 80 mm
    page_h = etiqueta_h

    final_pages = []

    for i in range(0, len(resized), 2):
        img1 = resized[i]
        img2 = resized[i+1] if i+1 < len(resized) else resized[i]

        # Página branca
        page_img = Image.new("RGB", (page_w, page_h), "white")

        # Centralização horizontal
        margin = int((page_w - (etiqueta_w * 2)) / 3)

        x1 = margin
        x2 = margin * 2 + etiqueta_w

        page_img.paste(img1, (x1, 0))
        page_img.paste(img2, (x2, 0))

        final_pages.append(page_img)

    # Salvar PDF final
    buffer = io.BytesIO()
    final_pages[0].save(buffer, format="PDF", save_all=True, append_images=final_pages[1:])
    buffer.seek(0)

    st.download_button(
        label="Baixar PDF Final (40×25 mm, 2 colunas)",
        data=buffer,
        file_name="etiquetas_40x25mm_duas_colunas.pdf",
        mime="application/pdf"
    )

    st.success("PDF gerado com sucesso!")
