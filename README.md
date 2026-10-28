# Web Plagiarism Analyzer

## Project Type
BTech CSE (AI/ML) Minor Project

## Overview

Web Plagiarism Analyzer is a local NLP-based application that accepts a PDF, DOCX, or TXT document and searches publicly accessible web pages for potentially similar text.

The system extracts the document text, divides it into sentences, searches for distinctive sentence content, retrieves accessible web pages, compares the student sentence with sentences from those pages, and generates a plagiarism-risk report.

The application is designed as a prototype for academic demonstration and manual verification.

## Main Features

- PDF, DOCX and TXT document support
- Automatic text extraction
- Sentence-level analysis
- Web source discovery
- Source-page retrieval
- TF-IDF lexical similarity
- Word-overlap analysis
- Combined similarity scoring
- Flagged sentence display
- Closest matching source sentence
- Retrieved source ranking
- Overall similarity percentage
- Low / Medium / High risk classification
- Local browser dashboard
- No deployment required
- No database required
- No API key required

## Project Architecture

```text
PDF / DOCX / TXT
       |
       v
Text Extraction
       |
       v
Text Cleaning
       |
       v
Sentence Segmentation
       |
       v
Distinctive Sentence Query
       |
       v
Public Web Search
       |
       v
Web Page Retrieval
       |
       v
Source Sentence Extraction
       |
       +----------------------+
       |                      |
       v                      v
TF-IDF Similarity       Word Overlap
       |                      |
       +----------+-----------+
                  |
                  v
          Combined Score
                  |
                  v
        Risk Classification
                  |
                  v
          Web Dashboard
```

## Technologies

- Python
- Flask
- scikit-learn
- BeautifulSoup
- Requests
- PyPDF2
- python-docx
- HTML
- CSS

## Installation

### 1. Install Python

Python 3.10 or newer is recommended.

### 2. Open the project folder

```bash
cd Web_Plagiarism_Analyzer_Final
```

### 3. Create a virtual environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

### 6. Open the application

Open:

```text
http://127.0.0.1:5000
```

## Demonstration

For a reliable demonstration:

1. Prepare a short TXT, DOCX or PDF containing 3–8 sentences.
2. Include a few sentences copied or closely paraphrased from publicly available pages.
3. Upload the document.
4. Click **Analyze for Similarity**.
5. Review the overall similarity and risk level.
6. Open the flagged sentence section.
7. Show the closest matching source text.
8. Open the source link to manually verify the match.

A short document is recommended because the prototype intentionally limits the number of sentences sent to web search.

## Similarity Method

The project uses a combined lexical similarity score.

### TF-IDF

TF-IDF converts text into numerical vectors based on the importance of words and word pairs.

The implementation uses:

```text
unigrams + bigrams
```

and English stop-word removal.

### Cosine Similarity

Cosine similarity measures the angle between the TF-IDF vectors.

A higher value means the two pieces of text contain more similar lexical patterns.

### Word Overlap

The system also calculates the percentage of meaningful words from the student sentence that occur in the candidate source sentence.

### Combined Score

The final sentence score is:

```text
Combined Score =
0.70 × TF-IDF Similarity
+
0.30 × Word Overlap
```

This gives more importance to the TF-IDF similarity while retaining a simple overlap signal.

## Risk Levels

```text
0–34%    Low
35–64%   Medium
65–100%  High
```

These thresholds are prototype thresholds for demonstration and are not official plagiarism standards.

## Why Sentence-Level Comparison?

Comparing a complete student document against an entire webpage can dilute a copied passage because the webpage may contain thousands of unrelated words.

This project therefore:

```text
Student sentence
       vs.
Source sentence candidates
```

and retains the closest matching source sentence.

This produces a more interpretable result for the user.

## Limitations

This project does NOT claim to search the entire Internet.

It searches public web results and attempts to retrieve accessible pages. Some websites may:

- block automated requests
- require JavaScript
- require login
- prevent scraping
- return incomplete content
- temporarily reject requests

Therefore, a source not being detected does not prove that the document is original.

Likewise, similarity does not prove academic plagiarism. Common facts, definitions, quotations, and standard terminology can naturally produce similar text.

The result should therefore be interpreted as:

> Potential textual similarity requiring manual verification.

## Important Technical Limitation

The current search layer uses public Google search-result HTML rather than a commercial search API. Search-result layouts can change, and automated requests can occasionally be blocked.

For a classroom prototype this keeps the project free and avoids requiring an API key.

## Privacy

Uploaded files are processed locally by the Flask application.

The extracted sentence queries are sent to the public search engine because web searching is part of the project functionality. Do not use confidential documents for demonstrations.

## Project Structure

```text
Web_Plagiarism_Analyzer_Final/
|
├── app.py
├── checker.py
├── requirements.txt
├── README.md
├── .gitignore
|
├── templates/
|   └── index.html
|
├── static/
|   └── style.css
|
└── uploads/
    └── .gitkeep
```

## Future Scope

Possible future improvements include:

- Sentence-BERT semantic similarity
- Search API integration
- Paraphrase detection using transformer models
- OCR for scanned PDFs
- Downloadable PDF reports
- Batch analysis of multiple submissions
- Source credibility scoring
- Better duplicate-source filtering
- Highlighting matching phrases directly inside the document

## Viva Summary

The project is an NLP-based web plagiarism-risk analyzer.

The input document is converted to text and split into sentences. Distinctive sentences are searched on the public web. Accessible source pages are retrieved and divided into sentences. Each student sentence is compared with source candidates using TF-IDF cosine similarity and word overlap. The highest matching source is retained. A combined similarity score is used to flag potentially copied content and classify the overall result into low, medium, or high risk.

The system is intended to assist manual plagiarism review rather than replace human judgment.
