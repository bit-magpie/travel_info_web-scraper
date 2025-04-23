import csv
from bs4 import BeautifulSoup
import re
import os

def extract_data(html_content):
    """Extract Top 100 places data from HTML content"""
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Dictionary to store our results
    results = {}
    
    # Find all fieldset tags which contain the category information
    fieldsets = soup.find_all('fieldset')
    
    for fieldset in fieldsets:
        # Extract category name
        legend = fieldset.find('legend')
        
        if legend:
            # Find the main category name (the green text)
            category_span = legend.find('span', style=lambda x: x and 'color:#22AA22' in x)
            if category_span:
                category_name = category_span.text.strip()
                
                # Find count (number in parentheses)
                count_match = re.search(r'\((\d+)\)', legend.text)
                count = int(count_match.group(1)) if count_match else 0
                
                # Find places
                places = []
                
                # Look for table rows
                rows = fieldset.find_all('tr')
                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 1:
                        place_cell = cells[0]
                        place_name = place_cell.text.strip()
                        
                        # Check if this is a comma-separated list
                        if ',' in place_name:
                            place_items = [item.strip() for item in place_name.split(',')]
                            for item in place_items:
                                places.append((item, ""))
                        else:
                            # If there's a second cell, it might contain location info
                            location = cells[1].text.strip() if len(cells) > 1 else ""
                            places.append((place_name, location))
                
                # Store in our results dictionary
                results[category_name] = {'count': count, 'places': places}
    
    # Get prefecture name from title
    prefecture = ""
    title_tag = soup.find('title')
    if title_tag:
        title_text = title_tag.text.strip()
        match = re.search(r"(\w+)'s best 100", title_text)
        if match:
            prefecture = match.group(1)
    
    return prefecture, results

def save_to_csv(prefecture, data, output_dir="output"):
    """Save the extracted data to CSV file"""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Prepare CSV filename
    filename = os.path.join(output_dir, f"{prefecture}_top_100.csv")
    
    # Write to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Prefecture', 'Category', 'Place', 'Location']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for category, info in data.items():
            for place, location in info['places']:
                writer.writerow({
                    'Prefecture': prefecture,
                    'Category': category,
                    'Place': place,
                    'Location': location
                })
    
    print(f"Data saved to {filename}")

def print_results(prefecture, data):
    """Print the extracted data in a readable format"""
    print(f"\n## {prefecture} Prefecture Top 100 Places")
    
    for category, info in data.items():
        print(f"\n- **{category} ({info['count']})**")
        for place, location in info['places']:
            if location:
                print(f"  - {place} ({location})")
            else:
                print(f"  - {place}")

def process_html_file(filepath, output_dir="output"):
    """Process a single HTML file"""
    with open(filepath, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    prefecture, data = extract_data(html_content)
    print_results(prefecture, data)
    save_to_csv(prefecture, data, output_dir)

def process_directory(directory_path, output_dir="output"):
    """Process all HTML files in a directory"""
    html_files = [f for f in os.listdir(directory_path) if f.endswith('.html')]
    
    for html_file in html_files:
        filepath = os.path.join(directory_path, html_file)
        print(f"Processing {filepath}...")
        process_html_file(filepath, output_dir)

def main():
    # Set input directory or file
    input_path = "./raw_html/"  # Current directory, change as needed
    output_dir = "output"
    
    # Check if input_path is a directory or file
    if os.path.isdir(input_path):
        process_directory(input_path, output_dir)
    elif os.path.isfile(input_path) and input_path.endswith('.html'):
        process_html_file(input_path, output_dir)
    else:
        print("Please provide a valid HTML file or directory containing HTML files")
        
        # Look for HTML files in current directory
        html_files = [f for f in os.listdir('.') if f.endswith('.html')]
        if html_files:
            print("\nFound HTML files in current directory:")
            for file in html_files:
                print(f"- {file}")
            file_to_process = html_files[0]  # Process the first file
            print(f"\nProcessing {file_to_process}...")
            process_html_file(file_to_process, output_dir)

if __name__ == "__main__":
    main()