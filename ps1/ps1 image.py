# Still developing, errors in the code
import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
from io import BytesIO
import pytesseract

def extract_text_from_image(image_url):
    response = requests.get(image_url)

    # Check if the content is an image
    if "image" not in response.headers["content-type"]:
        print("The provided URL does not point to an image.")
        return None

    # Use PIL to open the image from BytesIO
    img = Image.open(BytesIO(response.content))

    # Use pytesseract to extract text from the image
    text = pytesseract.image_to_string(img)

    return text

def analyze_terms(text, target_terms):
    term_results = {}

    # Iterate through each term
    for term in target_terms:
        term_results[term] = {"count_per_input": []}

        # Count the occurrences of the term in the text
        occurrences = len(re.findall(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE))

        # Update the results
        term_results[term]["count_per_input"].append(occurrences)

    return term_results

def analyze_terms_for_all(urls, target_terms):
    # Initialize a dictionary to store counts for each term and input
    all_results = {term: {"count_per_input": []} for term in target_terms}

    # Analyze terms for all entered URLs
    for i, url in enumerate(urls, start=1):
        # Send a GET request to the URL
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the HTML content of the page using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text from the HTML
            input_text = soup.get_text()

            # Analyze term occurrences
            term_results = analyze_terms(input_text, target_terms)

            # Accumulate counts for each term and input
            for term, details in term_results.items():
                all_results[term]["count_per_input"].extend(details["count_per_input"])

            # Extract text from images on the page
            images = soup.find_all('img')
            for image in images:
                image_url = image['src']
                image_text = extract_text_from_image(image_url)
                
                if image_text is not None:
                    term_results_image = analyze_terms(image_text, target_terms)
                    
                    for term_image, details_image in term_results_image.items():
                        all_results[term_image]["count_per_input"].extend(details_image["count_per_input"])

        else:
            print(f"Failed to retrieve data for URL {url}. Status code: {response.status_code}")

    # Calculate total counts for each term
    for term, details in all_results.items():
        details["total_count"] = sum(details["count_per_input"])

    return all_results

def display_summary(all_results):
    # Display the summarized output for each term only if count is greater than 0
    for term, details in all_results.items():
        if details["total_count"] > 0:
            print(f"\nTerm: {term}")
            print("\tOccurrences in each input:")
            for i, count in enumerate(details["count_per_input"], start=1):
                print(f"\tInput {i}: {count}")

            # Display the total count across all inputs
            print(f"\tTotal occurrences in all inputs: {details['total_count']}")
        else:
            print(f"\nTerm: {term}:\n\tNo occurrences in any input.")

# Take multiple inputs until the user enters '0'
user_inputs = []
while True:
    user_input = input("Enter a URL (enter '0' to stop): ")

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

# Analyze terms for all entered URLs and store the results
results = analyze_terms_for_all(user_inputs, filter_terms)

# Display the summarized output
display_summary(results)
