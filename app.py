import streamlit as st
import pdfplumber
import re
from PIL import Image
import io
import zipfile
import base64

def convert_pdf_to_markdown(pdf_file):
    markdown_content = ""
    image_files = []
    image_counter = 1

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            # Extraer texto
            text = page.extract_text()
            if text:
                # Procesar el texto para mantener el formato Markdown
                text = re.sub(r'^# (.+)$', r'# \1', text, flags=re.MULTILINE)  # Encabezados
                text = re.sub(r'\*\*(.+?)\*\*', r'**\1**', text)  # Negrita
                text = re.sub(r'_(.+?)_', r'*\1*', text)  # Cursiva
                
                markdown_content += text + "\n\n"
            
            # Extraer imágenes
            try:
                for image in page.images:
                    try:
                        image_bytes = image['stream'].get_data()
                        image_filename = f'imagen_{image_counter}.png'
                        
                        # Añadir referencia de la imagen al Markdown
                        markdown_content += f'![Imagen {image_counter}](ANEXOS/{image_filename})\n\n'
                        
                        # Guardar imagen en memoria
                        image_files.append((image_filename, image_bytes))
                        image_counter += 1
                    except Exception as img_error:
                        st.warning(f"No se pudo procesar una imagen: {str(img_error)}")
            except Exception as page_error:
                st.warning(f"No se pudieron procesar las imágenes de una página: {str(page_error)}")

    return markdown_content, image_files

def create_download_link(file_content, file_name):
    b64 = base64.b64encode(file_content).decode()
    return f'<a href="data:application/zip;base64,{b64}" download="{file_name}">Descargar archivo ZIP</a>'

st.title('Convertidor de PDF a Markdown')

uploaded_file = st.file_uploader("Elige un archivo PDF", type="pdf")

if uploaded_file is not None:
    if st.button('Convertir a Markdown'):
        with st.spinner('Convirtiendo...'):
            try:
                markdown_content, image_files = convert_pdf_to_markdown(uploaded_file)
                
                # Crear un archivo ZIP en memoria
                memory_file = io.BytesIO()
                with zipfile.ZipFile(memory_file, 'w') as zf:
                    zf.writestr("output.md", markdown_content)
                    for img_name, img_data in image_files:
                        zf.writestr(f"ANEXOS/{img_name}", img_data)
                
                memory_file.seek(0)
                
                if len(image_files) > 0:
                    st.success('Conversión completada con éxito!')
                else:
                    st.warning('La conversión se completó, pero no se encontraron imágenes en el PDF.')
                
                st.markdown(create_download_link(memory_file.getvalue(), 'markdown_output.zip'), unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f'Ocurrió un error durante la conversión: {str(e)}')

st.markdown("---")
st.write("Desarrollado con ❤️ usando Streamlit")