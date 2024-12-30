OpenCV (cv2): used for image processing tasks. In this project, it helps in handling image loading, resizing, and drawing bounding boxes around detected text.
NumPy: powerful library for numerical computations. It is used in this project to handle images as arrays, which is essential for OpenCV processing.
EasyOCR: optical character recognition (OCR) library that is used to detect and recognize text in images. It is particularly effective for detecting text in various fonts and noisy images.
Pytesseract: It is a Python wrapper for Google's Tesseract-OCR engine. It is used in this project to detect and extract text from images.
Gradio: library for creating interactive UIs for machine learning models. In this project, it is used to build a user interface that allows users to upload images, view OCR results, and compare outputs from EasyOCR and
Pytesseract.
CSV: Purpose: The csv module is used to write the OCR results into a CSV file for further analysis and comparison.
os: os module is used to handle file system operations such as checking and creating files or directories.
