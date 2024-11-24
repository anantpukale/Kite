import pdfplumber
import pandas as pd


# Function to extract pin names and their positions
def extract_text_with_position(pdf_page):
	text_data = []

	for char in pdf_page.extract_words():
		text_data.append({
			"text": char['text'],
			"x0": char['x0'],
			"top": char['top'],
			"x1": char['x1'],
			"bottom": char['bottom']
		})

	return pd.DataFrame(text_data)


# Function to associate pin names with their closest numbers based on proximity
def map_pins_to_numbers(text_df):
	pins = text_df[text_df['text'].str.contains(r'P\d+_\d+|EVCC|EVSS|VCC|VSS', regex=True)]
	numbers = text_df[text_df['text'].str.match(r'^\d+$')]

	associations = []

	for _, pin in pins.iterrows():
		# Calculate the distance between the pin and each number
		distances = ((numbers['x0'] - pin['x0']) ** 2 + (numbers['top'] - pin['top']) ** 2) ** 0.5

		# Find the nearest number
		nearest_number_index = distances.idxmin()
		nearest_number = numbers.loc[nearest_number_index, 'text']

		associations.append((pin['text'], nearest_number))

	return associations


# Path to the PDF
pdf_path = '10.pdf'

# Open the PDF and extract text from the first page
with pdfplumber.open(pdf_path) as pdf:
	page = pdf.pages[0]
	# Extract text along with their positions
	text_df = extract_text_with_position(page)

	# Map pin names to their closest numbers
	pin_mappings = map_pins_to_numbers(text_df)

	# Output the results
	for pin, number in pin_mappings:
		print(f"Pin: {pin}, Associated Number: {number}")
