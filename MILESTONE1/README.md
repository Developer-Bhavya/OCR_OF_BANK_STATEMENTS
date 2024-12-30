Technologies and Libraries Used
1) Web Scraping (Week 1)
   Languages: Python
     Libraries:
2) requests: For sending HTTP requests and fetching HTML
content.
3) BeautifulSoup (from bs4): For parsing and extracting image
URLs from HTML pages.
4)Concepts: Bing Image Search, Directory Management, Data
Downloading.
Key Features:
• Automated image scraping from Bing Image Search
• Organized directory structure for different document types
• Error handling for failed downloads
• Progress tracking and reporting

4)Cloud Storage and Retrieval 
• Platform: Cloudinary :  Used for securely storing and managing images in the cloud.
  Languages: Python
    Libraries: cloudinary and cloudinary.api: For interacting with the Cloudinary API.
5) Install required packages:
pip install requests beautifulsoup4 cloudinary
Configuration: Web Scraping Setup
No additional configuration required. The script
automatically creates necessary directories.
Cloudinary Setup:
Configure your Cloudinary credentials:
cloudinary.config(
cloud_name="your_cloud_name",
api_key="your_api_key",
api_secret="your_api_secret"
)
