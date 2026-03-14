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

    # Converte cada página em imagem
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        imagens.append(img)

    # Reduzir para 37,5×25 mm (aprox 142×95 px a 96 DPI)
    resized = [img.resize((142, 95), Image.LANCZOS) for img in imagens]

    # Criar páginas com 2 etiquetas lado a lado
    final_pages = []
    for i in range(0, len(resized), 2):
        img1 = resized[i]
        img2 = resized[i+1] if i+1 < len(resized) else resized[i]

        # Página branca 303×95 px (80×25 mm)
        page_img = Image.new("RGB", (303, 95), "white")
        page_img.paste(img1, (0, 0))
        page_img.paste(img2, (161, 0))

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
