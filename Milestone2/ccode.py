import gradio as gr
import easyocr
import cohere
import matplotlib.pyplot as plt
import tempfile
import os
import cv2
import re
import cloudinary
import cloudinary.api
import requests
from collections import defaultdict
from fuzzywuzzy import fuzz
import pandas as pd
from io import BytesIO

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Configure Cloudinary
cloudinary.config(
    cloud_name="deg42enyf",
    api_key="942296943917836",
    api_secret="sw3uVuzO4jxc8sEo4KWB1rk5p24"
)

# Configure Cohere
COHERE_API_KEY = os.getenv("t8xZLFJFQeVzqkyueWyuufSVs1HqWav1vwboefHJ", "Enter your cohere api key")
cohere_client = cohere.Client(COHERE_API_KEY)

# Field definitions
field_names = {
    "payslip": {
        "Basic Salary": ["Basic Salary", "Basic Pay", "Basic", "Basic Wage"],
        "HRA": ["HRA", "House Rent Allowance", "Housing Allowance"],
        "DA": ["DA", "Dearness Allowance"],
        "Total Earnings": ["Total Earnings", "Gross Salary", "Gross Pay"],
        "Net Pay": ["Net Pay", "Take Home", "Net Salary"],
        "Tax Deductions": ["TDS", "Tax Deducted", "Income Tax"]
    },
    "Balancesheets": {
        "Total Assets": ["Total Assets", "Assets", "Net Assets"],
        "Total Liabilities": ["Total Liabilities", "Liabilities", "Net Liabilities"],
        "Current Assets": ["Current Assets", "Current Asset"],
        "Fixed Assets": ["Fixed Assets", "Fixed Asset"],
        "Current Liabilities": ["Current Liabilities", "Current Liability"],
        "Shareholders Equity": ["Shareholders Equity", "Share Capital", "Equity"]
    },
    "Bankstatements": {
        "Opening Balance": ["Opening Balance", "Beginning Balance", "Start Balance"],
        "Closing Balance": ["Closing Balance", "Ending Balance", "Final Balance"],
        "Total Credits": ["Total Credits", "Sum of Credits", "Total Deposits"],
        "Total Debits": ["Total Debits", "Sum of Debits", "Total Withdrawals"],
        "Average Balance": ["Average Balance", "Avg Balance"],
        "Minimum Balance": ["Minimum Balance", "Min Balance"]
    }
}

def get_images_by_prefix(prefix_list, num_images):
    try:
        result = cloudinary.api.resources(
            type="upload",
            resource_type="image",
            max_results=500
        )
        matching_images = []
        for resource in result.get('resources', []):
            public_id = resource.get('public_id', '')
            if any(public_id.startswith(prefix) for prefix in prefix_list):
                matching_images.append(resource['secure_url'])
        matching_images.sort()
        return matching_images[:num_images]
    except Exception as e:
        print(f"Error getting images: {e}")
        return []

def download_image(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(response.content)
                return tmp.name
        return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

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

def is_valid_numeric(value):
    value = value.replace(",", "").replace("$", "").replace("\u20b9", "")
    return bool(re.match(r'^\d+(\.\d+)?$', value))

def is_similar(text, variations, threshold=70):
    text = text.lower().strip()
    for variation in variations:
        score = fuzz.partial_ratio(text, variation.lower().strip())
        if score >= threshold:
            return True
    return False

def get_highest_lowest_values(image_data, fields):
    analysis = {}
    for field in fields:
        values = []
        for img_idx, data in image_data.items():
            if field in data:
                try:
                    value = float(data[field].replace(",", "").replace("$", "").strip())
                    values.append((value, img_idx))
                except ValueError:
                    continue
        if values:
            max_value, max_idx = max(values, key=lambda x: x[0])
            min_value, min_idx = min(values, key=lambda x: x[0])
            analysis[field] = {
                "highest": f"{max_value:,.2f} (Image {max_idx + 1})",
                "lowest": f"{min_value:,.2f} (Image {min_idx + 1})"
            }
    return analysis

def analyze_images(folder_name, num_images, chart_type):
    prefix_map = {
        "Balancesheets": ["Balance_Sheet", "Balance_sheet"],
        "Bankstatements": ["Image_"],
        "payslip": ["payslip", "P_L"]
    }

    image_urls = get_images_by_prefix(prefix_map[folder_name], num_images)
    if not image_urls:
        return "No images found", None, None, "No data to display", "No comparison data available", None

    image_data = defaultdict(dict)
    selected_fields = field_names[folder_name]
    downloaded_images = []

    for img_idx, url in enumerate(image_urls):
        img_path = download_image(url)
        if img_path:
            downloaded_images.append(img_path)
            preprocessed_path = preprocess_image(img_path)
            if preprocessed_path:
                results = reader.readtext(preprocessed_path)
                for idx, (_, text, _) in enumerate(results):
                    cleaned_text = text.strip()
                    for field, variations in selected_fields.items():
                        if is_similar(cleaned_text, variations):
                            for offset in range(idx + 1, len(results)):
                                potential_value = results[offset][1].strip()
                                if is_valid_numeric(potential_value):
                                    image_data[img_idx][field] = potential_value
                                    break

    # Create table data
    table_data = []
    headers = ["Image"] + list(selected_fields.keys())
    for img_idx in range(len(downloaded_images)):
        row = [f"Image {img_idx+1}"]
        for field in selected_fields:
            row.append(image_data[img_idx].get(field, "N/A"))
        table_data.append(row)

    # Create DataFrame
    df = pd.DataFrame(table_data, columns=headers)

    # Create visualization
    fig, ax = plt.subplots(figsize=(10, 8))
    colors = plt.cm.tab10.colors

    if chart_type == "Bar Chart":
        x = range(len(downloaded_images))
        bar_width = 0.2
        for i, (field, _) in enumerate(selected_fields.items()):
            values = [float(image_data[idx].get(field, "0").replace(",", "")) 
                     for idx in range(len(downloaded_images))]
            ax.bar(
                [xi + i * bar_width for xi in x],
                values,
                bar_width,
                label=field,
                color=colors[i % len(colors)]
            )
        ax.set_xticks([xi + bar_width * (len(selected_fields) - 1) / 2 for xi in x])
        ax.set_xticklabels([f"Image {i+1}" for i in x])
        ax.set_xlabel("Images")
        ax.set_ylabel("Values")
        ax.legend()
    elif chart_type == "Pie Chart":
        values = []
        labels = []
        for img_idx in range(len(downloaded_images)):
            for field in selected_fields:
                if field in image_data[img_idx]:
                    value = float(image_data[img_idx][field].replace(",", ""))
                    values.append(value)
                    labels.append(f"Image {img_idx+1} - {field}")
        if values:
            ax.pie(values, labels=labels, autopct='%1.1f%%', colors=colors)

    # Save chart
    chart_path = tempfile.mktemp(suffix='.png')
    plt.savefig(chart_path)
    plt.close()

    # Get value comparison
    value_comparison = get_highest_lowest_values(image_data, selected_fields.keys())
    comparison_text = "Value Comparison Analysis:\n\n"
    for field, values in value_comparison.items():
        comparison_text += f"{field}:\n"
        comparison_text += f"  Highest: {values['highest']}\n"
        comparison_text += f"  Lowest: {values['lowest']}\n\n"

    # Create CSV file for download
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp_csv:
        df.to_csv(temp_csv.name, index=False)
        csv_file_path = temp_csv.name

    return (
        f"Successfully processed {len(downloaded_images)} images",
        image_urls,
        chart_path,
        df.to_string(index=False),
        comparison_text,
        csv_file_path
    )

def clear_outputs():
    return (None, 3, "Bar Chart", "", None, "", None, "", None)

def create_interface():
    with gr.Blocks(css="""
    .gradio-container {background-color: black; color: white;}
    .gradio-container label {color: orange;}
    button {background-color: orange !important; color: black !important;}
    button:hover {background-color: darkorange !important; color: white !important;}
    .table {border: 2px solid orange; color: orange;}
    """) as demo:
        gr.Markdown("# Document Analysis System")
        
        with gr.Row():
            folder_input = gr.Dropdown(
                choices=["payslip", "Balancesheets", "Bankstatements"],
                label="Document Type",
                value="payslip"
            )
            num_images = gr.Number(
                label="Number of Images",
                value=3,
                minimum=1,
                maximum=10,
                step=1
            )
            chart_type = gr.Radio(
                ["Bar Chart", "Pie Chart"],
                label="Chart Type",
                value="Bar Chart"
            )

        with gr.Row():
            analyze_btn = gr.Button("Analyze Documents")
            clear_btn = gr.Button("Clear All")
        
        with gr.Row():
            status = gr.Textbox(label="Status")
        
        with gr.Row():
            gallery = gr.Gallery(label="Retrieved Images")
        
        with gr.Row():
            table_output = gr.Textbox(label="Extracted Data", lines=10)
        
        with gr.Row():
            chart_output = gr.Image(label="Visualization")
        
        with gr.Row():
            comparison_output = gr.Textbox(label="Value Comparison", lines=10)
        
        with gr.Row():
            download_output = gr.File(label="Download Extracted Data")

        analyze_btn.click(
            analyze_images,
            inputs=[folder_input, num_images, chart_type],
            outputs=[status, gallery, chart_output, table_output, comparison_output, download_output]
        )

        clear_btn.click(
            clear_outputs,
            inputs=[],
            outputs=[folder_input, num_images, chart_type, status, gallery, 
                    table_output, chart_output, comparison_output, download_output]
        )

        return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(share=True)
