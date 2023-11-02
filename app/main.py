import logging
import os
import shutil
from datetime import timedelta
from io import BytesIO
from typing import List
import firebase_admin
import pandas as pd
from fastapi import FastAPI, Response, Depends, File, Request, HTTPException, Body, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from firebase_admin import credentials, storage
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette.responses import FileResponse
from . import models, schemas
from .database import engine, get_db
from .models import Image, ProductVariant
from .routes import on_boarding, inventory, profile, branches, products, employee, billing_system, company

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

app.include_router(on_boarding.router)
app.include_router(inventory.router)
app.include_router(profile.router)
app.include_router(branches.router)
app.include_router(products.router)
app.include_router(company.router)
app.include_router(billing_system.router)
app.include_router(employee.router)

UPLOAD_DIR = "app/images"
logging.basicConfig(filename='app.log', level=logging.DEBUG)


def save_image_to_db(db, filename, file_path):
    image = Image(filename=filename, file_path=file_path)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {'storageBucket': 'onecart-6156a.appspot.com',
                                     'databaseURL': 'https://onecart-6156a-default-rtdb.firebaseio.com/'})

