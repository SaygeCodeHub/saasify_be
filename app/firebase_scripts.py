import os
import shutil
from typing import List

import firebase_admin
from fastapi import UploadFile, File, APIRouter
from starlette.responses import JSONResponse

from firebase_admin import firestore, credentials, storage

router = APIRouter()
cred = credentials.Certificate("saasify-de974-firebase-adminsdk-q7lul-e6555891c4.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

directory = "app/uploaded_images"
if not os.path.exists(directory):
    os.makedirs(directory)


def save_upload_file(upload_file: UploadFile, destination: str):
    try:
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()


@router.post("/v1/uploadImages")
async def upload_images(upload_files: List[UploadFile] = File(...)):
    image_urls = []
    for upload_file in upload_files:
        destination = os.path.join("app", "uploaded_images", upload_file.filename)
        save_upload_file(upload_file, destination)
        bucket = storage.bucket()
        bucket.cors = [
            {
                "origin": ["*"],
                "responseHeader": [
                    "Content-Type",
                    "x-goog-resumable"],
                "method": ['PUT', 'POST', 'GET'],
                "maxAgeSeconds": 3600
            }
        ]
        bucket.patch()
        blob = bucket.blob(f"uploaded_images/{upload_file.filename}")
        blob.upload_from_filename(destination)
        image_url = blob.public_url

        image_urls.append(image_url)
    response_data = {
        "status": 200,
        "message": "Images uploaded successfully.",
        "data": image_urls}
    return JSONResponse(content=response_data)


def master_config():
    modules = {
        "HRMS": {
            "name": "HRMS",
            "baseCost": 2000,
        },
        "POS": {
            "name": "POS",
            "baseCost": 1000,
        },
        "Inventory Management": {
            "name": "Inventory Management",
            "baseCost": 1000,
        },
        "Finance": {
            "name": "Finance",
            "baseCost": 500,
        },
    }

    for module_id, module_data in modules.items():
        module_ref = db.collection("modules").document(module_id)
        module_ref.set(module_data)

    print("Master configuration successfully created in Firestore!")


def add_firebase_client(clientId: str, activate: bool):
    print("here===========add_firebase_client")
    new_client_ref = db.collection("clients").document(clientId)
    client_data = {}
    selected_modules = ["HRMS", "POS"]

    for module_id in selected_modules:
        module_ref = db.collection("modules").document(module_id)
        module_data = module_ref.get().to_dict()
        if module_data:
            client_data[module_id] = {
                "name": module_data.get("name", ""),
                "baseCost": module_data.get("baseCost", 0)}

    client_data["activateBackend"] = activate
    new_client_ref.set(client_data)
