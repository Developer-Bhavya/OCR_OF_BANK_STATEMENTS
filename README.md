#  BFSI OCR & Financial Analysis System

A robust AI-powered system that automates the extraction and analysis of financial data from bank statements using OCR and LLMs, offering actionable insights into income and expenses. Designed for use by banks, fintech platforms, and individuals for streamlined financial intelligence.

---

##  Project Objective

This project aims to automate the extraction and analysis of key financial information from bank statements using:

- 🧾 Optical Character Recognition (OCR) for reading document images  
- 🤖 LLMs for understanding and structuring extracted text  
- 🔗 APIs for fetching real-time statements  
- 📊 Visual analytics to present data insights

---

##  Key Features

-  Automated text extraction from scanned bank statements  
-  Salary and expense analysis with insightful visualizations  
-  API integration for real-time document retrieval  
-  Cloud-based storage and processing of documents  
-  Structured outputs in tabular format  

---

##  Tech Stack & Libraries Used

| Library        | Description |
|----------------|-------------|
| **Gradio**     | User interface for uploading documents and visualizing results |
| **EasyOCR**    | Optical character recognition engine |
| **Cohere**     | Natural Language Processing for text understanding |
| **Cloudinary** | Cloud storage and image retrieval via prefix-based search |
| **Matplotlib** | Chart and graph generation for financial visualization |
| **OpenCV**     | Image preprocessing (grayscale, noise reduction, thresholding) |
| **Pandas**     | Tabular data structuring and financial comparison |
| **FuzzyWuzzy** | Fuzzy matching for text similarity |
| **Tempfile**   | Temporary file handling during processing |
| **OS**         | File operations and environment variable management |
| **Requests**   | HTTP requests for image download and processing |
| **re**         | Regular expressions for data validation and extraction |

---

## 🧩 Project Modules & Milestones

###  Milestone 1: API Integration (Weeks 1–2)
- Securely fetch bank statements via APIs

### Milestone 2: OCR & Data Extraction (Weeks 3–5)
- Extract data from diverse formats using OCR and LLMs

###  Milestone 3: Salary & Expense Analysis (Weeks 6–8)
- Categorize income vs. expenses and generate analytical summaries

###  Milestone 4: Deployment & Integration (Weeks 9–12)
- Full deployment with real-time platform integration

---

## Sample Output

-  Pie charts and bar graphs showing financial trends  

---

##  Security Considerations

-  API keys stored securely via environment variables  
-  Temporary files are cleaned post-processing  
-  Secure communication with cloud and third-party services

---

##  Getting Started

```bash
# Clone the repository
git clone https://github.com/your-username/bfsi-ocr-project.git
cd bfsi-ocr-project

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
