import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db.models import FileField, ImageField, DateField
from main.models import *
import zipfile
import os
from VehicleDelivery.settings import LOGGING

logger = LOGGING.getLogger("logger")


def export_single_object(request, obj_id, model):
    obj = get_object_or_404(model, id=obj_id)

    # Create a new workbook and worksheet
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Complaint Data"

    # Get all field names, excluding FileField and ImageField
    fields = [field for field in model._meta.fields if not isinstance(field, (FileField, ImageField))]
    headers = [field.name for field in fields]
    worksheet.append(headers)

    # Apply styling to headers
    header_fill = PatternFill(start_color="B3D9FF", end_color="B3D9FF", fill_type="solid")
    for col_num, header_cell in enumerate(worksheet[1], 1):
        header_cell.font = Font(bold=True)
        header_cell.alignment = Alignment(horizontal="center")
        header_cell.fill = header_fill

    values = []
    for field in fields:
        value = getattr(obj, field.name)

        # If the field is a DateField, convert it to a string for correct formatting
        if isinstance(field, DateField) and value:
            value = value.strftime("%Y-%m-%d")  # Format dates

        values.append(value)

    worksheet.append(values)

    # Auto-adjust column widths with a max limit
    MAX_COLUMN_WIDTH = 25  # Set a max width (characters)
    for col_num, col_cells in enumerate(worksheet.columns, 1):
        max_length = 0
        col_letter = openpyxl.utils.get_column_letter(col_num) 
        for cell in col_cells:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        adjusted_width = min(max_length + 2, MAX_COLUMN_WIDTH)  # Apply max width limit
        worksheet.column_dimensions[col_letter].width = adjusted_width

    # Prepare response
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="complaint_{obj_id}.xlsx"'

    workbook.save(response)

    logger.info(f"User {request.user} is downloading files for object {obj_id}")
    logger.debug(f"User {request.user} is downloading files for object {obj_id}")
    return response



def download_all_files(request, obj_id, model):
    obj = get_object_or_404(model, id=obj_id)

    # Collect all file fields
    file_fields = [
        field.name for field in obj._meta.fields 
        if isinstance(field, (models.FileField, models.ImageField))
    ]
    
    # Collect existing files
    files = [getattr(obj, field) for field in file_fields if getattr(obj, field)]

    # If no files, return an error response
    if not files:
        return HttpResponse("No files available for download.", content_type="text/plain")

    # Create ZIP file
    response = HttpResponse(content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="documents_{obj_id}.zip"'

    with zipfile.ZipFile(response, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in files:
            file_path = file.path 
            if os.path.exists(file_path):
                zip_file.write(file_path, f"{obj_id}_{os.path.basename(file_path)}")

    return response
