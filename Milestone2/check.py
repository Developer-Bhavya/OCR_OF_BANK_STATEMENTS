import os
import re
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from easyocr import Reader
import gradio as gr
from cloudinary import api, config
import requests
from io import BytesIO
import pandas as pd  # Added for handling tabular data

# Configure Cloudinary
config(
    cloud_name="dmwxgv4iv",
    api_key="618415941598468",
    api_secret="Ssc5Z92R6jXsH7ScreydHdTRNos"
)

# Initialize the EasyOCR reader for English language
reader = Reader(['en'])

# Preprocessing function to enhance image for OCR
def preprocess_image(image):
    try:
        # Ensure the image is in grayscale mode
        image = image.convert("L")  # Convert to grayscale
        image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
        image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)  # Resize for clarity
        image = ImageEnhance.Contrast(image).enhance(2)  # Enhance contrast
        return image
    except Exception as e:
        raise Exception(f"Error during preprocessing: {str(e)}")

# Fetch images from Cloudinary folder with pagination support
import random
import time

def fetch_images_from_cloudinary(folder_name, num_images):
    try:
        image_urls = []
        next_cursor = None
        total_images_fetched = 0

        while len(image_urls) < num_images:
            # Fetch images in pages, max 100 per page
            print(f"Fetching images from Cloudinary... Current total: {len(image_urls)}")
            response = api.resources(type="upload", prefix=folder_name, max_results=100, next_cursor=next_cursor)

            # Debugging: Print the response to see the raw data
            print("Raw Cloudinary response:", response)

            # Extract URLs from the fetched resources
            image_urls.extend([resource['secure_url'] for resource in response['resources']])
            total_images_fetched += len(response['resources'])

            # Debugging: Print the number of images fetched in this iteration
            print(f"Fetched {len(response['resources'])} images from this page.")

            # Check if there are more images to fetch
            next_cursor = response.get('next_cursor', None)

            # Stop if there are no more images or if we have fetched enough
            if not next_cursor or len(image_urls) >= num_images:
                break

            # Add a delay to avoid hitting API rate limits (if any)
            time.sleep(1)

        # Debugging: Print the total number of images fetched across pages
        print(f"Total images fetched (after pagination): {total_images_fetched}")

        # If there are not enough images, print a warning
        if len(image_urls) < num_images:
            print(f"Warning: Only {len(image_urls)} images were fetched. Fewer than {num_images} available.")

        # Shuffle the image URLs and return the requested number
        random.shuffle(image_urls)
        return image_urls[:num_images]  # Limit to the required number of images

    except Exception as e:
        raise Exception(f"Error fetching images from Cloudinary: {str(e)}")

# Function to perform OCR and extract relevant information
def perform_ocr_from_cloudinary(folder_name, num_images, document_type):
    extracted_data = []
    extracted_values = []  # To store numeric values for statistics calculation

    try:
        # Fetch images from Cloudinary
        image_urls = fetch_images_from_cloudinary(folder_name, num_images)

        # Debugging: print the image URLs fetched
        print(f"Image URLs fetched: {image_urls}")

        for url in image_urls:
            try:
                # Download the image
                response = requests.get(url)
                image = Image.open(BytesIO(response.content))

                # Preprocess the image
                preprocessed_image = preprocess_image(image)

                # Perform OCR with EasyOCR
                ocr_result = reader.readtext(np.array(preprocessed_image))

                # Convert OCR result into a single string of text
                text = " ".join([result[1] for result in ocr_result])  # Extract text from OCR results

                image_name = url.split("/")[-1]  # Get image name from URL

                # Check for document types
                if document_type == "Pay Slip":
                    # Look for variations of 'Basic Salary' using regex
                    pattern = r"[Bb][Aa][Ss][Ii][Cc]\s*[Ss][Aa][Ll][Aa][Rr][Yy][^\d](\d[\d,](?:\.\d{1,2})?)"
                    match = re.search(pattern, text)
                    if match:
                        basic_salary = match.group(1)  # Extract the salary amount
                        extracted_data.append([image_name, "Basic Salary", basic_salary])
                        extracted_values.append(float(basic_salary.replace(',', '').replace('₹', '').strip()))
                    else:
                        extracted_data.append([image_name, "Basic Salary", "Not Found"])

                elif document_type == "Profit Loss Statement" and folder_name == "Profit":
                    # Look for variations of 'Total Expenses' using regex
                    pattern = r"[Tt][Oo][Tt][Aa][Ll]\s*[Ee][Xx][Pp][Ee][Nn][Ss][Ee][Ss][^\d](\d[\d,](?:\.\d{1,2})?)"
                    match = re.search(pattern, text)
                    if match:
                        total_expenses = match.group(1)  # Extract the expenses amount
                        extracted_data.append([image_name, "Total Expenses", total_expenses])
                        extracted_values.append(float(total_expenses.replace(',', '').strip()))
                    else:
                        extracted_data.append([image_name, "Total Expenses", "Not Found"])

                elif document_type == "Bank Statement" and folder_name == "BankStatement":
                    # Look for variations of 'Ending Balance' using regex
                    pattern = r"[Ee][Nn][Dd][Ii][Nn][Gg]\s*[Bb][Aa][Ll][Aa][Nn][Cc][Ee][^\d](\d[\d,](?:\.\d{1,2})?)"
                    match = re.search(pattern, text)
                    if match:
                        ending_balance = match.group(1)  # Extract the ending balance
                        extracted_data.append([image_name, "Ending Balance", ending_balance])
                        extracted_values.append(float(ending_balance.replace(',', '').strip()))
                    else:
                        extracted_data.append([image_name, "Ending Balance", "Not Found"])

            except Exception as e:
                extracted_data.append([url, "Error", str(e)])

    except Exception as e:
        return f"Error during OCR processing: {str(e)}"

    if not extracted_data:
        return "No relevant information found in the provided images."

    # Convert extracted data to a DataFrame for tabular display
    df = pd.DataFrame(extracted_data, columns=["Image Name", "Document Type", "Amount"])

    # Calculate statistics (Highest, Lowest, Average)
    if extracted_values:
        highest_value = max(extracted_values)
        lowest_value = min(extracted_values)
        average_value = np.mean(extracted_values)
        stats_data = [
            ["Highest Value", f"₹{highest_value:,.2f}"],
            ["Lowest Value", f"₹{lowest_value:,.2f}"],
            ["Average Value", f"₹{average_value:,.2f}"]
        ]
        stats_df = pd.DataFrame(stats_data, columns=["Statistic", "Value"])
        return df.to_html(index=False) + stats_df.to_html(index=False)

    return df.to_html(index=False)

# Gradio interface function
def gradio_interface(folder_name, num_images, document_type):
    return perform_ocr_from_cloudinary(folder_name, num_images, document_type)

# Set up Gradio interface with Cloudinary integration
iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Cloudinary Folder Name", placeholder="Enter Cloudinary folder name"),
        gr.Number(label="Number of Images to Fetch", value=5),
        gr.Dropdown(choices=["Pay Slip", "Profit Loss Statement", "Bank Statement"], label="Document Type")
    ],
    outputs=gr.HTML(label="OCR Output (Tabular)"),
    title="Cloudinary Document OCR",
    description="Fetch images from a Cloudinary folder, process them, and extract relevant information like 'Basic Salary', 'Total Expenses', or 'Ending Balance' from documents."
)

# Launch the Gradio app
if __name__ == "__main__":

    iface.launch()