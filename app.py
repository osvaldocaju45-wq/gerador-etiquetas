import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import io

st.title("Gerador de Etiquetas 40×25 mm – Zebra ZD220")
st.write("Envie o PDF original da Shopee (60×40 mm). O app gera um PDF com duas etiquetas por página, reduzidas para 37,5×25 mm.")

uploaded_file = st.file_uploader("Envie o PDF original", type=["pdf"])

if uploaded_file:
    reader = PdfReader(uploaded_file)
    pages = []

    # Extrair cada página como imagem
    for page in reader.pages:
        x_object = page["/Resources"]["/XObject"].get_object()
        for obj in x_object:
            if x_object[obj]["/Subtype"] == "/Image":
                data = x_object[obj]._data
                width = x_object[obj]["/Width"]
                height = x_object[obj]["/Height"]
                mode = "RGB" if x_object[obj]["/ColorSpace"] == "/DeviceRGB" else "P"

                img = Image.frombytes(mode, (width, height), data)
                pages.append(img)

    # Reduzir para 37,5×25 mm (aprox 142×95 px a 96 DPI)
    resized = []
    for img in pages:
        resized.append(img.resize((142, 95), Image.LANCZOS))

    # Criar PDF final com 2 etiquetas por página
    output = PdfWriter()

    for i in range(0, len(resized), 2):
        img1 = resized[i]
        img2 = resized[i+1] if i+1 < len(resized) else resized[i]

        # Criar página branca 80×25 mm (aprox 303×95 px)
        page_img = Image.new("RGB", (303, 95), "white")
        page_img.paste(img1, (0, 0))
        page_img.paste(img2, (161, 0))

        # Converter para PDF
        buffer = io.BytesIO()
        page_img.save(buffer, format="PDF")
        buffer.seek(0)

        page_reader = PdfReader(buffer)
        output.add_page(page_reader.pages[0])

    # Baixar PDF final
    final_buffer = io.BytesIO()
    output.write(final_buffer)
    final_buffer.seek(0)

    st.download_button(
        label="Baixar PDF Final (40×25 mm, 2 colunas)",
        data=final_buffer,
        file_name="etiquetas_40x25mm_duas_colunas.pdf",
        mime="application/pdf"
    )

    st.success("PDF gerado com sucesso!")
