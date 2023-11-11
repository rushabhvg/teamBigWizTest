import requests
from bs4 import BeautifulSoup
import re
import fitz

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF.
    """
    with fitz.open(pdf_path) as pdf_document:
        text = ""
        for page_number in range(pdf_document.page_count):
            page = pdf_document[page_number]
            text += page.get_text()
    return text

def analyze_terms(text, target_terms):
    """
    Analyzes the occurrences of target terms in the provided text.

    Args:
        text (str): Text to analyze.
        target_terms (list): List of terms to search for.

    Returns:
        dict: Results of term analysis.
    """
    term_results = {}

    for term in target_terms:
        term_results[term] = {"count_per_input": []}
        occurrences = len(re.findall(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE))
        term_results[term]["count_per_input"].append(occurrences)

    return term_results

def analyze_terms_for_all(inputs, target_terms):
    """
    Analyzes terms for all entered inputs.

    Args:
        inputs (list): List of URLs or file paths.
        target_terms (list): List of terms to search for.

    Returns:
        dict: Results of term analysis for all inputs.
    """
    all_results = {term: {"count_per_input": []} for term in target_terms}

    for i, input_data in enumerate(inputs, start=1):
        try:
            if input_data.startswith("http"):
                response = requests.get(input_data)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                soup = BeautifulSoup(response.content, 'html.parser')
                input_text = soup.get_text()
            elif input_data.lower().endswith(".pdf"):
                input_text = extract_text_from_pdf(input_data)
            else:
                input_text = input_data

            term_results = analyze_terms(input_text, target_terms)

            for term, details in term_results.items():
                all_results[term]["count_per_input"].extend(details["count_per_input"])

        except requests.exceptions.RequestException as e:
            print(f"Error retrieving data for {input_data}: {e}")

    for term, details in all_results.items():
        details["total_count"] = sum(details["count_per_input"])

    return all_results

def display_summary(all_results):
    for term, details in all_results.items():
        if details["total_count"] > 0:
            print(f"\nTerm: {term}")
            print("\tOccurrences in each input:")
            for i, count in enumerate(details["count_per_input"], start=1):
                print(f"\tInput {i}: {count}")
            print(f"\tTotal occurrences in all inputs: {details['total_count']}")
        else:
            print(f"\nTerm: {term}\n\tNo occurrences in any input.")

# MAIN PROGRAM

user_inputs = []

while True:
    user_input = input("Enter a URL or PDF path (enter '0' to stop): ")
    if user_input == '0':
        break
    user_inputs.append(user_input)

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
