import gradio as gr
import easyocr
import cohere
import matplotlib.pyplot as plt
import tempfile
import os
import cv2
import re
from collections import defaultdict
from fuzzywuzzy import fuzz

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Securely load the API key
COHERE_API_KEY = os.getenv("t8xZLFJFQeVzqkyueWyuufSVs1HqWav1vwboefHJ", "Enter your cohere api key")
cohere_client = cohere.Client(COHERE_API_KEY)

# Preprocess image for OCR
def preprocess_image(img_path):
    try:
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        image = cv2.fastNlMeansDenoising(image, None, 30, 7, 21)
        processed_image = cv2.convertScaleAbs(image, alpha=1.5, beta=0)
        processed_image = cv2.adaptiveThreshold(
            processed_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        processed_path = f"{img_path}_processed.png"
        cv2.imwrite(processed_path, processed_image)
        return processed_path
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None

# Function to check numeric validity
def is_valid_numeric(value):
    value = value.replace(",", "").replace("$", "").replace("\u20b9", "")
    return bool(re.match(r'^\d+(\.\d+)?$', value))

# Function to check text similarity
def is_similar(text, variations, threshold=70):
    text = text.lower().strip()
    for variation in variations:
        score = fuzz.partial_ratio(text, variation.lower().strip())
        if score >= threshold:
            return True
    return False

# Extract and visualize data
def extract_and_visualize(image_files, doc_type, chart_type):
    # Define the fields for different document types
    field_names = {
        "pay_slips": {"Basic Salary": ["Basic Salary", "Basic Pay", "Basic", "Basic Wage"]},
        "balance_sheets": {"Total Assets": ["Total Assets", "Assets", "Net Assets"],
                           "Total Liabilities": ["Total Liabilities", "Liabilities", "Net Liabilities"]},
        "bank_statement": {"Ending Balance": ["Ending Balance", "Closing Balance", "Final Balance"]},
    }

    selected_fields = field_names.get(doc_type, {})
    image_data = defaultdict(lambda: {field: "NULL" for field in selected_fields})

    # Loop through all uploaded images
    for img_idx, img_file in enumerate(image_files):
        try:
            # Read image from the temporary file path
            if isinstance(img_file, str):  # Check if already a file path
                img_path = img_file
            else:
                img_path = img_file.name

            preprocessed_path = preprocess_image(img_path)
            if not preprocessed_path:
                continue

            # Perform OCR using EasyOCR
            results = reader.readtext(preprocessed_path)

            # Extract relevant fields from OCR results
            for idx, (_, text, _) in enumerate(results):
                cleaned_text = text.strip()
                for field, variations in selected_fields.items():
                    if is_similar(cleaned_text, variations):
                        for offset in range(idx + 1, len(results)):
                            potential_value = results[offset][1].strip()
                            if is_valid_numeric(potential_value):
                                image_data[img_idx][field] = potential_value
                                break

        except Exception as e:
            print(f"Error processing image: {e}")

    # Visualization
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.tab10.colors
    field_values = defaultdict(list)

    for img_idx in range(len(image_files)):
        for field in selected_fields.keys():
            field_values[field].append(image_data[img_idx].get(field, "NULL"))

    if chart_type == "Bar Chart":
        x = range(len(image_files))
        bar_width = 0.2
        for i, (field, values) in enumerate(field_values.items()):
            ax.bar(
                [xi + i * bar_width for xi in x],
                [float(value.replace(",", "")) if value != "NULL" else 0 for value in values],
                bar_width,
                label=field,
                color=colors[i % len(colors)]
            )
        ax.set_xticks([xi + bar_width * (len(field_values) - 1) / 2 for xi in x])
        ax.set_xticklabels([f"Image {i+1}" for i in x])
        ax.set_xlabel("Uploaded Images")
        ax.set_ylabel("Extracted Values")
        ax.legend(title="Fields")

    elif chart_type == "Pie Chart":
        labels, sizes = [], []
        for img_idx, fields in image_data.items():
            for field, value in fields.items():
                if value != "NULL":
                    labels.append(f"Image {img_idx + 1} - {field}")
                    sizes.append(float(value.replace(",", "")))

        if sizes:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
            ax.set_title("Proportional Comparison of Extracted Values")

    plt.tight_layout()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
        chart_path = tmpfile.name
        plt.savefig(chart_path)
        plt.close()

    # Prepare summary
    summary = "Extracted data per image:\n"
    for img_idx, fields in image_data.items():
        summary += f"Image {img_idx + 1}:\n"
        for field, value in fields.items():
            summary += f" {field}: {value}\n"

    return summary, chart_path

# Gradio Interface
with gr.Blocks(css="""
.gradio-container {background-color: black; color: white;}
.gradio-container label {color: orange;}
button#component-2 {background-color: orange; color: black; font-weight: bold; border: none; border-radius: 5px; padding: 10px;}
button#component-2:hover {background-color: darkorange; color: white;}
button#component-3 {background-color: orange; color: black; font-weight: bold; border: none; border-radius: 5px; padding: 10px;}
button#component-3:hover {background-color: darkorange; color: white;}
textarea {border: 2px solid orange; color: orange;}
input[type=file] {border: 2px solid orange; color: orange;}
.radio {color: orange !important;}
.radio label {color: orange;}
.radio input {color: orange;}
img {border: 2px solid orange;}
""") as demo:
    gr.Markdown("<h1 style='text-align: center; color: white;'>OCR Data Extraction Tool</h1>")
    gr.Markdown("<p style='text-align: center; color: gray;'>Upload images, select a document type, and visualize the extracted data with a bar or pie chart.</p>")

    with gr.Row():
        doc_type = gr.Radio(
            ["balance_sheets", "pay_slips", "bank_statement"], 
            label="Document Type", 
            info="Select the type of document being processed"
        )

    with gr.Row():
        images = gr.File(label="Upload Images", file_types=[".jpg", ".png", ".jpeg"], file_count="multiple")
        chart_type = gr.Radio(["Bar Chart", "Pie Chart"], label="Chart Type")

    submit_btn = gr.Button("Extract and Visualize", elem_id="component-2")
    clear_btn = gr.Button("Clear All ", elem_id="component-3")

    with gr.Row():
        output_text = gr.Textbox(label="Extracted Data", interactive=False)
    with gr.Row():
        output_chart = gr.Image(label="Visualization")

    submit_btn.click(
        extract_and_visualize, 
        inputs=[images, doc_type, chart_type], 
        outputs=[output_text, output_chart]
    )

    def clear_fn():
        return None, "balance_sheets", "Bar Chart", "", None

    clear_btn.click(fn=clear_fn, inputs=[], outputs=[images, doc_type, chart_type, output_text, output_chart])

demo.launch()