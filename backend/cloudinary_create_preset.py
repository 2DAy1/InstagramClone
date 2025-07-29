from dotenv import load_dotenv
import os

import cloudinary
import cloudinary.api

load_dotenv(".env.dev")

cloudinary.config(
    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key = os.getenv('CLOUDINARY_API_KEY'),
    api_secret = os.getenv('CLOUDINARY_API_SECRET'),
)


upload_preset_name = "my_preset"
upload_preset_options = {
    "unsigned": False,
    "folder": "instagram_clone",
    "tags": "post,avatar",
    "transformation": [
        {"width": 500, "height": 500, "crop": "fill"},
        {"effect": "grayscale"},
    ],
    "categorization": "aws_rek_tagging",
    "auto_tagging": 0.9
}


upload_preset = cloudinary.api.create_upload_preset(
    name=upload_preset_name,
    settings=upload_preset_options
)

if upload_preset.get("name") == upload_preset_name:
    print("Upload preset created successfully.")
else:
    print("Failed to create upload preset.")
