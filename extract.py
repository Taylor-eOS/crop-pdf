from PyPDF2 import PdfReader

def extract_and_save_text_from_pdf(pdf_path, output_file):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)

        with open(output_file, 'w', encoding='utf-8') as text_file:
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                # Remove page numbers (assuming they are at the bottom)
                lines = page_text.split('\n')
                lines = [line for line in lines if not line.strip().isdigit()]
                # Join lines ending with a hyphen to the next line
                for i, line in enumerate(lines):
                    if i < len(lines) - 1 and line.endswith('-'):
                        lines[i + 1] = line[:-1] + lines[i + 1]
                    else:
                        text_file.write(line + " ")
                text_file.write("\n")  # Add a line break after each page
                # Add an additional line break if the last line was short
                if len(lines[-1]) < 0.9 * sum(len(line) for line in lines) / max(len(lines), 1):
                    text_file.write("\n")

            text_file.write("\n")  # Add an extra line break after processing all pages

if __name__ == "__main__":
    pdf_path = "test.pdf"  # Replace with the actual file name or path
    output_file = "output.txt"

    extract_and_save_text_from_pdf(pdf_path, output_file)

    print(f"Text extracted from {pdf_path} and saved to {output_file}")

