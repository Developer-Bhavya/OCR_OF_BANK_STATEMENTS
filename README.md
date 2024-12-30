# OCR-Of-Bank-Statements
The system provides an automated solution to analyze financial and document data, extract relevant information, and generate visual insights using llm model. 
1. Gradio: Provides a user-friendly interface to interact with the system. Designed the front-end for the user to upload inputs, visualize results,and retrieve outputs seamlessly.
2. EasyOCR : Optical Character Recognition (OCR) for text extraction from images.
3. Cohere: NLP capabilities for advanced text analysis. Configuration: Initialized with the Cohere API key.
5. Cloudinary: Handles cloud storage and retrieval of document images. Retrieves image URLs using a prefix-based search.  Securely downloads and processes images for analysis.
6. Matplotlib: Visualization of extracted data. Generates bar and pie charts based on extracted values. Enhances user understanding of financial metrics.
7. OpenCV : Image preprocessing for OCR enhancement. Applied grayscale conversion, noise reduction, and adaptive thresholding.  Improves OCR accuracy for low-quality documents.
8. Cloudinary API : Secure interaction with cloud-hosted resources.
9. Pandas : Tabular representation of extracted data. Organizes the data into a user-friendly format. Supports creation of comparison tables.
10. FuzzyWuzzy : Text similarity checking using fuzzy matching.
11. Tempfile: Temporary file management during processing.
12. OS: Environment variable management and file operations.
13. Requests: HTTP requests for downloading images from URLs. Retrieves images and saves them temporarily for OCR.
14.Re : Regular expressions for data validation.
