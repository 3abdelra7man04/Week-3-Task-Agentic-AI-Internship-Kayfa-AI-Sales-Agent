import os
from os.path import join
from json_repair import repair_json
from glob import glob
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance

import base64

from openai import OpenAI
from models.enums.MyPDFLoaderEnum import MyPDFLoaderEnum
from helpers.config import get_settings
import json
from ..schemes.page_scheme import PageScheme


def preprocess_image(image, max_width = 600):
  # convert image to greyscale
  gray_img = image.convert("L")

  # resize and keep aspect ratio
  if gray_img.width > max_width:
    image_original_width, image_original_height = image.size
    image_aspect_ratio = image_original_width / image_original_height
    new_height = int(max_width / image_aspect_ratio)

    gray_img = gray_img.resize((max_width, new_height))

  # increase the contrast of the image
  gray_img = ImageEnhance.Contrast(gray_img).enhance(1.5)

  # return image
  return gray_img

def convert_pdf_to_images(pdf_path, output_base_dir, max_width = 600, dpi = 200):
  # retrieve pdf name
  pdf_name = os.path.basename(pdf_path)
  pdf_name = os.path.splitext(pdf_name)[0]

  # create directory of pdf name for the converted images
  path = os.path.join(output_base_dir, pdf_name)
  os.makedirs(path, exist_ok= True)
  generated_paths = []
  # convert pdf to images
  images = convert_from_path(pdf_path=pdf_path, dpi=dpi)

  # total number of pages
  total_pages = 0

  # preprocess and save the images
  for i, image in enumerate(images):
    preprocessed_image = preprocess_image(image)
    image_path = os.path.join(path, f"page {i}.jpeg")
    preprocessed_image.save(image_path, "JPEG")
    
    generated_paths.append(image_path)

    total_pages+=1

  return generated_paths, total_pages

def image_to_base64_data_uri(image_path):

    """Convert image to base64 data URI for APIs"""
    with open(image_path, 'rb') as image_file:
        img_base64 = base64.b64encode(image_file.read()).decode('utf-8')

    # Determine image type from extension
    ext = image_path.lower().split('.')[-1]
    mime_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"

    return f"data:{mime_type};base64,{img_base64}"


def extract_pages(file_path,  output_base_dir, max_width = 600, dpi = 200):

    images_paths, total_pages = convert_pdf_to_images(file_path, output_base_dir, max_width, dpi)

    pages_dicts = []
    

    # Model Client 
    client = OpenAI(
    base_url= MyPDFLoaderEnum.BASE_URL.value,
    api_key= get_settings().OPENAI_API_KEY,
    )


    for page_num, path in enumerate(images_paths, start=1):

        # model inout message
        messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": MyPDFLoaderEnum.OCR_PROMPT.value},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_to_base64_data_uri(path)
                    }
                }

            ]
        }
        ]

        # First API call with reasoning
        response = client.chat.completions.create(
        model= MyPDFLoaderEnum.OCR_MODEL.value,
        messages= messages,
        max_tokens = MyPDFLoaderEnum.MAX_OUTPUT_TOKENS.value,
        response_format= {
            "type": "json_schema",
            "json_schema": {
                "name": "page_schema",
                "strict": True,
                "schema": PageScheme.model_json_schema()
            }
        }
        )

        # Extract the assistant message with reasoning_details
        try:
          response = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError as e:
            print(f"Detected broken JSON, attempting repair... page:{page_num}")
            repaired_string = repair_json(response.choices[0].message.content)
            response = json.loads(repaired_string)
            raise e
        

        # add the source, file path, page, total_pages metadata
        response["metadata"]["source"] = file_path
        response["metadata"]["file_path"] = file_path
        response["metadata"]["page"] = page_num
        response["metadata"]["total_pages"] = total_pages

        pages_dicts.append(response)

    return pages_dicts
