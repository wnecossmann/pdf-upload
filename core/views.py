# === views.py ===
import os
import fitz  # PyMuPDF
import shutil
from uuid import uuid4
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings
from django.shortcuts import render

@csrf_exempt
def upload_pdf(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        temp_dir = os.path.join(settings.MEDIA_ROOT, str(uuid4()))
        os.makedirs(temp_dir, exist_ok=True)

        # Speichere hochgeladene Datei
        pdf_path = os.path.join(temp_dir, uploaded_file.name)
        with open(pdf_path, 'wb+') as dest:
            for chunk in uploaded_file.chunks():
                dest.write(chunk)

        # PDF verarbeiten
        doc = fitz.open(pdf_path)
        output_folder = os.path.join(temp_dir, "extracted")
        os.makedirs(output_folder, exist_ok=True)

        for i, page in enumerate(doc):
            text = page.get_text("text")
            lines = text.split("\n")
            owner_name = f"Seite_{i+1}"
            for j, line in enumerate(lines):
                if "Grundstückseigentümer" in line:
                    if j + 1 < len(lines):
                        owner_name = lines[j + 1].strip().replace(" ", "_").replace("/", "_")
                    break

            output_pdf_path = os.path.join(output_folder, f"{owner_name}.pdf")
            rotated_doc = fitz.open()
            rotated_page = rotated_doc.new_page(width=page.rect.height, height=page.rect.width)
            rotated_page.show_pdf_page(rotated_page.rect, doc, i, rotate=90)
            rotated_doc.save(output_pdf_path)
            rotated_doc.close()

        # ZIP erstellen
        zip_path = os.path.join(temp_dir, "output.zip")
        shutil.make_archive(zip_path.replace(".zip", ""), 'zip', output_folder)

        return JsonResponse({"download_url": f"/download/?path={zip_path}"})
    return JsonResponse({"error": "Kein PDF erhalten."}, status=400)


def download_zip(request):
    path = request.GET.get("path")
    if not path or not os.path.exists(path):
        return JsonResponse({"error": "Datei nicht gefunden."}, status=404)
    return FileResponse(open(path, 'rb'), as_attachment=True, filename="extracted_pages.zip")


def index(request):
    return render(request, 'index.html')
