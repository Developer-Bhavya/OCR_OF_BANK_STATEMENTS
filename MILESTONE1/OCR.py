import cv2
import numpy as np
import easyocr
import pytesseract
import gradio as gr
import csv
import os

# Example function to detect and recognize text using EasyOCR and Pytesseract
def detect_and_recognize(image, min_size, text_threshold, low_txt, link_threshold):
    # Initialize OCR models
    easyocr_reader = easyocr.Reader(['en'])
    
    # EasyOCR text detection and recognition
    easyocr_output = easyocr_reader.readtext(image)
    easyocr_boxes = [box[0] for box in easyocr_output]
    easyocr_text = [box[1] for box in easyocr_output]
    
    # Pytesseract text detection and recognition
    pytesseract_output = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    pytesseract_boxes = []
    pytesseract_text = []
    
    for i in range(len(pytesseract_output['text'])):
        if int(pytesseract_output['conf'][i]) > 0:  # Only consider text with positive confidence
            pytesseract_boxes.append((
                pytesseract_output['left'][i],
                pytesseract_output['top'][i],
                pytesseract_output['left'][i] + pytesseract_output['width'][i],
                pytesseract_output['top'][i] + pytesseract_output['height'][i]
            ))
            pytesseract_text.append(pytesseract_output['text'][i])
    
    return {
        'EasyOCR': {'boxes': easyocr_boxes, 'text': easyocr_text},
        'Pytesseract': {'boxes': pytesseract_boxes, 'text': pytesseract_text}
    }

# Function to draw bounding boxes on the image
def draw_boxes(image, easyocr_boxes, pytesseract_boxes):
    easyocr_image = image.copy()
    pytesseract_image = image.copy()

    for box in easyocr_boxes:
        pts = np.array(box, np.int32)
        pts = pts.reshape((-1, 1, 2))
        easyocr_image = cv2.polylines(easyocr_image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
    
    for box in pytesseract_boxes:
        pts = np.array([[box[0], box[1]], [box[2], box[1]], [box[2], box[3]], [box[0], box[3]]], np.int32)
        pts = pts.reshape((-1, 1, 2))
        pytesseract_image = cv2.polylines(pytesseract_image, [pts], isClosed=True, color=(255, 0, 0), thickness=2)
    
    return easyocr_image, pytesseract_image

# Function to compare OCR results with EasyOCR and Pytesseract
def compare_ocr(image, min_size, text_threshold, low_txt, link_threshold, canvas_size):
    # Ensure that canvas_size is a tuple of two positive integers
    if isinstance(canvas_size, tuple) and len(canvas_size) == 2:
        width, height = canvas_size
        if width > 0 and height > 0:
            image = cv2.resize(image, (width, height))  # Resize the image if canvas_size is valid
    else:
        # Handle the case where canvas_size is invalid
        print("Invalid canvas size. No resizing applied.")
    
    # Convert the image to a format that OpenCV can use (numpy array)
    image = np.array(image)
    
    # Get OCR results
    output = detect_and_recognize(image, min_size, text_threshold, low_txt, link_threshold)
    
    # Draw bounding boxes for both OCR methods
    easyocr_image, pytesseract_image = draw_boxes(image, output['EasyOCR']['boxes'], output['Pytesseract']['boxes'])
    
    # Prepare text results for both OCR methods
    text_results_easyocr = [[str(i + 1), text] for i, text in enumerate(output['EasyOCR']['text'])]
    text_results_pytesseract = [[str(i + 1), text] for i, text in enumerate(output['Pytesseract']['text'])]
    
    # Save text results to CSV
    csv_filename = "ocr_results.csv"
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "EasyOCR Text", "Pytesseract Text"])
        for easyocr_text, pytesseract_text in zip(text_results_easyocr, text_results_pytesseract):
            writer.writerow([easyocr_text[0], easyocr_text[1], pytesseract_text[1]])
    
    # Return images with bounding boxes, text results, and the CSV file
    return easyocr_image, pytesseract_image, text_results_easyocr, text_results_pytesseract, csv_filename

# Gradio interface for user interaction
def create_interface():
    # Parameters for OCR
    min_size = gr.Slider(minimum=1, maximum=10, value=5, label="Minimum Size")
    text_threshold = gr.Slider(minimum=0, maximum=1, step=0.01, value=0.5, label="Text Threshold")
    low_txt = gr.Slider(minimum=0, maximum=1, step=0.01, value=0.4, label="Low Text Threshold")
    link_threshold = gr.Slider(minimum=0, maximum=1, step=0.01, value=0.4, label="Link Threshold")
    canvas_size = gr.Slider(minimum=1, maximum=1000, step=1, value=500, label="Canvas Size", interactive=True)
    
    # Gradio interface with a submit button
    iface = gr.Interface(
        fn=compare_ocr,
        inputs=[
            gr.Image(type="numpy", label="Upload Image"), 
            min_size, 
            text_threshold, 
            low_txt, 
            link_threshold, 
            canvas_size
        ],
        outputs=[
            gr.Image(type="numpy", label="EasyOCR Bounded Image"), 
            gr.Image(type="numpy", label="Pytesseract Bounded Image"), 
            gr.Dataframe(label="EasyOCR Text Results"), 
            gr.Dataframe(label="Pytesseract Text Results"), 
            gr.File(label="Download CSV")
        ],
        live=False  # Disable live processing, use submit button instead
    )
    return iface

# Run the interface
iface = create_interface()
iface.launch(share=True)
