\# AI Billing \& Freight Audit Assistant — MVP



\## ✅ Overview

This project is a \*\*Streamlit web app\*\* that parses \*\*FedEx Freight invoices\*\* (CSV, XLSX, or PDF) and extracts:

\- \*\*Freight Bill Number\*\*

\- \*\*Line Items\*\* (main shipment charges)

\- \*\*Accessorial Charges\*\* (e.g., Fuel Surcharge, Liftgate, Redelivery)

\- \*\*Total Amount Due\*\*



It uses:

\- \*\*pdfplumber\*\* for text-based PDFs

\- \*\*Tesseract OCR\*\* for scanned PDFs

\- \*\*Regex\*\* for structured data extraction



---



\## ✅ Features

\- Upload FedEx Freight invoices in \*\*CSV, XLSX, or PDF\*\* format.

\- Extract and display:

&nbsp; - \*\*Total Amount Due\*\*

&nbsp; - \*\*Line Items\*\* in a table

&nbsp; - \*\*Accessorial Charges\*\* in a separate table

\- Download parsed data as \*\*CSV\*\*.

\- Lightweight logging for audit runs.



---



\## ✅ Live Demo

https://ai-billing-assistant-9klkoa8x4khml6ghzguiz7.streamlit.app/



---



\## ✅ Tech Stack

\- Python 3.10+

\- Streamlit

\- pdfplumber

\- pytesseract

\- Pillow

\- pandas



---



\## ✅ How to Run Locally

1\. Clone the repo:

&nbsp;  ```bash

&nbsp;  git clone https://github.com/<your-username>/fedex-freight-audit-mvp.git

&nbsp;  cd fedex-freight-audit-mvp



2\. Install dependencies:



pip install -r requirements.txt



3\. Install Tesseract:



Windows: https://github.com/UB-Mannheim/tesseract/wiki

Mac: brew install tesseract

Linux: sudo apt-get install tesseract-ocr



4\. Run the app

streamlit run app.py



Deploy on Streamlit Cloud



Push your code to GitHub.

Add packages.txt with:

tesseract-ocr





Go to https://streamlit.io/cloud, connect your repo, and deploy.

Your app will be live at a public URL.



Project Structure

/project-root

&nbsp; ├── app.py

&nbsp; ├── parsers/

&nbsp; │    └── file\_parser.py

&nbsp; ├── exporters/

&nbsp; │    └── csv\_export.py

&nbsp; ├── requirements.txt

&nbsp; ├── packages.txt

&nbsp; ├── .gitignore

&nbsp; └── refs/

