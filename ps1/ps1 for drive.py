import requests
import io
import fitz  # PyMuPDF library for PDF processing
import re

def extract_text_from_pdf_url(pdf_url):
    # Download the PDF file from the internet
    response = requests.get(pdf_url)

    if response.status_code == 200:
        # Extract text from the downloaded PDF content
        pdf_content = io.BytesIO(response.content)
        with fitz.open(pdf_content) as pdf_document:
            text = ""
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                text += page.get_text()

        return text
    else:
        print(f"Failed to retrieve PDF data from {pdf_url}. Status code: {response.status_code}")
        return None

def analyze_terms(input_text, terms):
    results = {}

    # Iterate through each term
    for term in terms:
        results[term] = {"count": 0}

        # Count the occurrences of the term in the input text
        occurrences = len(re.findall(r'\b' + re.escape(term) + r'\b', input_text, re.IGNORECASE))

        # Update the results
        results[term]["count"] = occurrences

    return results

def analyze_terms_for_all(inputs, terms):
    all_results = {term: {"count": 0} for term in terms}

    for i, input_data in enumerate(inputs, start=1):
        if input_data.lower().startswith("http"):
            # If the input is a URL, fetch data from the web
            input_text = extract_text_from_pdf_url(input_data)
        elif input_data.lower().endswith(".pdf"):
            # If the input is a local PDF file, extract text offline
            with open(input_data, 'rb') as pdf_file:
                pdf_content = io.BytesIO(pdf_file.read())
                with fitz.open(pdf_content) as pdf_document:
                    input_text = ""
                    for page_number in range(pdf_document.page_count):
                        page = pdf_document[page_number]
                        input_text += page.get_text()
        else:
            # Assume the input is plain text
            input_text = input_data

        # Analyze term occurrences
        term_results = analyze_terms(input_text, terms)

        # Accumulate counts for each term and input
        for term, details in term_results.items():
            all_results[term]["count"] += details["count"]

    return all_results

def display_summary(all_results):
    for term, details in all_results.items():
        if details["count"] > 0:
            print(f"\nTerm: {term}")
            print(f"\tTotal occurrences in all inputs: {details['count']}\n")

# Take multiple inputs until the user enters '0'
user_inputs = []
while True:
    user_input = input("Enter a URL, PDF path, or plain text (enter '0' to stop): ")

    if user_input == '0':
        break

    user_inputs.append(user_input)

# Define the terms to filter
filter_terms = [
    "Shrinkflation",
    "Stagnant",
    "Pandemic",
    "Conflict",
    "Unemployment",
    "Turmoil",
    "Reform",
    "Dutch Disease",
    "Purchasing Power Parity"
]

# Analyze terms for all entered inputs and store the results
results = analyze_terms_for_all(user_inputs, filter_terms)

# Display the summarized output
display_summary(results)
