from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List
import os
import tempfile

from app.services.document_processor import DocumentProcessor
from app.services.form_filler import fill_form

router = APIRouter()

@router.post("/process_documents/")
async def process_documents(
    files: List[UploadFile] = File(...)
):
    temp_file_paths = []
    bol_path = "/Users/khushalidaga/Downloads/Bill-Of-Lading.pdf"
    invoice_path = "/Users/khushalidaga/Downloads/Invoice-Packing-List.xlsx"
    try:
        for file in files:
            # Save uploaded file temporarily
            temp_file = tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.filename)[1], delete=False)
            temp_file_path = temp_file.name
            temp_file_paths.append(temp_file_path)

            # Write content to temp file
            content = await file.read()
            temp_file.write(content)
            temp_file.close()
            
            # Classify file based on extension
            if file.filename.lower().endswith('.pdf'):
                bol_path = "/Users/khushalidaga/Downloads/Bill-Of-Lading.pdf"
            elif file.filename.lower().endswith(('.xlsx', '.xls')):
                invoice_path = "/Users/khushalidaga/Downloads/Invoice-Packing-List.xlsx"

        # Ensure we have both required files
        if not bol_path or not invoice_path:
            raise HTTPException(status_code=400, detail="Please provide both a PDF bill of lading and an Excel commercial invoice")

        # Process documents - create an instance first
        processor = DocumentProcessor()
        # Call the process_documents method with correct parameters
        extracted_data = processor.process_documents(bol_path, invoice_path)
        # Fill form
        success = fill_form(extracted_data)

        return {"success": success}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")
    
    finally:
        # Clean up temp files
        for path in temp_file_paths:
            try:
                os.unlink(path)
            except:
                pass

# @router.post("/upload-documents/")
# async def upload_documents(
#     background_tasks: BackgroundTasks,
#     bill_of_lading: UploadFile = File(...),
#     commercial_invoice: UploadFile = File(...)
# ):
#     """
#     Upload a bill of lading PDF and commercial invoice Excel file
#     for processing customs information.
#     """
#     # Validate file types
#     if not bill_of_lading.filename.endswith('.pdf'):
#         raise HTTPException(status_code=400, detail="Bill of lading must be a PDF file")
    
#     if not commercial_invoice.filename.endswith(('.xlsx', '.xls')):
#         raise HTTPException(status_code=400, detail="Commercial invoice must be an Excel file")
    
#     # Create temp directory for processing
#     temp_dir = tempfile.mkdtemp()
    
#     try:
#         # Save uploaded files
#         bol_path = os.path.join(temp_dir, bill_of_lading.filename)
#         invoice_path = os.path.join(temp_dir, commercial_invoice.filename)
        
#         # Write files to disk
#         with open(bol_path, "wb") as bol_file:
#             bol_content = await bill_of_lading.read()
#             bol_file.write(bol_content)
            
#         with open(invoice_path, "wb") as invoice_file:
#             invoice_content = await commercial_invoice.read()
#             invoice_file.write(invoice_content)
        
#         # Initialize document processor
#         processor = DocumentProcessor()
        
#         # Store files for processing (you might want to save in DB or pass to queue)
#         document_data = {
#             "bill_of_lading_path": bol_path,
#             "commercial_invoice_path": invoice_path,
#             "bill_of_lading_name": bill_of_lading.filename,
#             "commercial_invoice_name": commercial_invoice.filename,
#         }
        
#         # Add cleanup task to remove temp files after processing
#         background_tasks.add_task(cleanup_temp_files, temp_dir)
#         print(document_data)
#         return {
#             "status": "success",
#             "message": "Files uploaded successfully",
#             "document_data": document_data
#         }
    
#     except Exception as e:
#         # Ensure cleanup happens even on error
#         cleanup_temp_files(temp_dir)
#         raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

def cleanup_temp_files(temp_dir):
    """Remove temporary files after processing"""
    import shutil
    try:
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error cleaning up temporary files: {str(e)}")