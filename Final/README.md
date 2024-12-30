Technologies and Libraries Used
1. Gradio:
   Purpose: Provides a user-friendly interface to interact with the system.
   Usage: Designed the front-end for the user to upload inputs, visualize results,  and retrieve outputs seamlessly.
2. EasyOCR :
  Purpose: Optical Character Recognition (OCR) for text extraction from images.
 Features: Supports multiple languages (here, en for English).
 Usage: Detects and extracts text from images after preprocessing.  Maps text to predefined categories such as "Basic Salary," "HRA," etc.
4. Cohere:
 Purpose: NLP capabilities for advanced text analysis.
 Configuration: Initialized with the Cohere API key.
 Usage: Placeholder for potential language-based enrichment tasks.
5. Cloudinary:
 Purpose: Handles cloud storage and retrieval of document images.
 Usage: Retrieves image URLs using a prefix-based search. Securely downloads and processes images for analysis.
6. Matplotlib:
 Purpose: Visualization of extracted data.
 Features: Generates bar and pie charts based on extracted values. Enhances user understanding of financial metrics.
7. OpenCV :
 Purpose: Image preprocessing for OCR enhancement.
 Usage: Applied grayscale conversion, noise reduction, and adaptive thresholding. Improves OCR accuracy for low-quality documents.
8. Cloudinary API :
 Purpose: Secure interaction with cloud-hosted resources.
 Usage: Queries cloud storage to retrieve financial document images by prefix.
9. Pandas :
 Purpose: Tabular representation of extracted data.
 Features: Organizes the data into a user-friendly format. Supports creation of comparison tables.
10. FuzzyWuzzy : Purpose: Text similarity checking using fuzzy matching.
 Features: Matches text in the document to predefined field names with variations. Configurable similarity threshold (default: 70%).
11. Tempfile:
 Purpose: Temporary file management during processing.
 Usage: Stores intermediate files like processed images and visualizations.
12. OS:
 Purpose: Environment variable management and file operations.
Usage: Accesses API keys and file paths.
12.Requests:
 Purpose: HTTP requests for downloading images from URLs.
usage: Retrieves images and saves them temporarily for OCR.
13.Re :
 Purpose: Regular expressions for data validation.
 Usage:Ensures extracted values are numeric or formatted correctly
