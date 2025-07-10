from flask import Request, jsonify, request
from google.cloud import vision
import io
from pdf2image import convert_from_bytes
from PIL import Image
import os
import functions_framework

@functions_framework.http
def season_ocr_http(request: Request):
    files = request.files.getlist("files")
    client = vision.ImageAnnotatorClient()
    results = []

    for file in files:
        try:
            content = file.read()
            filename = os.path.basename(file.filename).strip().lower()

            # txtファイルはそのまま読み取り
            if filename.endswith(".txt"):
                text = content.decode("utf-8")

            # PDFは画像に変換して、各ページOCR
            elif filename.endswith(".pdf"):
                images = convert_from_bytes(content, dpi=300)
                text_chunks = []
                for page_num, image in enumerate(images):
                    img_io = io.BytesIO()
                    image.save(img_io, format="PNG")
                    image_bytes = img_io.getvalue()

                    image_vision = vision.Image(content=image_bytes)
                    response = client.document_text_detection(
                        image=image_vision,
                        image_context={"language_hints": ["ja"]},
                    )
                    page_text = response.full_text_annotation.text.strip()
                    text_chunks.append(page_text if page_text else f"(Page {page_num+1}: No text)")

                text = "\n\n".join(text_chunks)

            # 画像系（PNG, JPGなど）
            else:
                image = vision.Image(content=content)
                response = client.document_text_detection(
                    image=image,
                    image_context={"language_hints": ["ja"]},
                )
                text = response.full_text_annotation.text.strip() if response.full_text_annotation.text else "(No text found)"

            results.append({
                "filename": file.filename,
                "text": text
            })

        except Exception as e:
            results.append({
                "filename": file.filename,
                "text": f"OCRエラー：{str(e)}"
            })

    print("Uploaded files (raw):", request.files)

    return jsonify({"results": results})
