# 🧾 AI Billing & Freight Audit Assistant — MVP

## ✅ Overview
This project is a **Streamlit web app** that parses **FedEx Freight invoices** (CSV, XLSX, or PDF) and extracts:

- **Freight Bill Number**
- **Line Items** (main shipment charges)
- **Accessorial Charges** (e.g., Fuel Surcharge, Liftgate, Redelivery)
- **Total Amount Due**

It uses:
- **pdfplumber** for text-based PDFs  
- **Tesseract OCR** for scanned PDFs  
- **Regex** for structured data extraction  

---

## ✅ Features
- Upload FedEx Freight invoices in **CSV, XLSX, or PDF** format.  
- Extract and display key data:
  - **Total Amount Due**
  - **Line Items** in a table
  - **Accessorial Charges** in a separate table  
- Download parsed data as **CSV**.  
- Lightweight logging for audit runs.  

---

## ✅ Live Demo
[🔗 Open in Streamlit Cloud](https://ai-billing-assistant-9klkoa8x4khml6ghzguiz7.streamlit.app/)

---

## ✅ Tech Stack
- Python **3.11** (recommended for Streamlit Cloud)  
- Streamlit  
- pdfplumber  
- pytesseract  
- Pillow  
- pandas  

---

## ✅ How to Run Locally

1. **Clone the repo**
   ```bash
   git clone https://github.com/<your-username>/ai-billing-assistant.git
   cd ai-billing-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Tesseract (for OCR support)**
   - **Windows:** [Tesseract-OCR (UB Mannheim build)](https://github.com/UB-Mannheim/tesseract/wiki)
   - **Mac:** `brew install tesseract`
   - **Linux:** `sudo apt-get install tesseract-ocr`

4. **Run the app locally**
   ```bash
   streamlit run app.py
   ```

---

## ✅ Deployment Requirements (Streamlit Cloud)

To ensure the app builds and runs correctly on Streamlit Cloud:

1. **Python version**
   - Streamlit Cloud defaults to Python 3.13, which may break some libraries.  
   - Pin Python 3.11 manually by doing **one** of the following:
     - In **Manage App → Settings → Python Version**, select **3.11**, **or**
     - Add a root-level file named `runtime.txt` containing:
       ```
       3.11
       ```

2. **Required root-level files**
   ```
   requirements.txt     # Python dependencies
   packages.txt         # Optional OS packages
   runtime.txt          # Forces Python 3.11
   app.py               # Streamlit entry point
   ```

3. **Example `requirements.txt`**
   ```txt
   pip>=24.0
   setuptools>=68.0.0
   wheel>=0.41.0
   streamlit==1.39.0
   pandas==2.2.2
   pdfplumber==0.11.0
   python-dotenv
   openai
   langchain
   pillow==10.4.0
   ```

4. **Example `packages.txt`** (optional for PDF/OCR support)
   ```txt
   poppler-utils
   tesseract-ocr
   ```

5. **Force a rebuild**
   Whenever dependencies change:
   ```bash
   git add .
   git commit -m "Update dependencies"
   git push
   ```
   Then in Streamlit Cloud, go to **Manage App → Reboot**.

---

## ✅ Project Structure
```
/project-root
├── app.py
├── parsers/
│   └── file_parser.py
├── exporters/
│   └── csv_export.py
├── requirements.txt
├── packages.txt
├── runtime.txt
├── .gitignore
└── refs/
    └── audit_log.jsonl
```

---

## ✅ (Optional) Screenshot
You can include a visual of your deployed app:
```markdown
![AI Billing Assistant Demo](./refs/demo_screenshot.png)
```

---

## ✅ Credits
Developed by **Terrence Wright**  
FedEx Freight Transportation Intermediary Team  
Executive MBA Candidate — Baylor University  

---

## ✅ License
This project is open-source under the MIT License.
