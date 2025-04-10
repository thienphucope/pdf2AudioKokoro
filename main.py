import os
from pdf_processing import process_pdf
from text_splitting import process_text
from tts_processing import process_text_to_audio
from audio_merging import merge_audio

def get_valid_pdf_path():
    """Prompts the user for a PDF path and validates it."""
    while True:
        pdf_path = input('Enter the path to your PDF file (e.g., "/path/to/file.pdf"): ').strip()
        pdf_path = pdf_path.strip('"').strip("'")
        if not os.path.exists(pdf_path):
            print(f"Error: File '{pdf_path}' does not exist. Please try again.")
        elif not pdf_path.lower().endswith('.pdf'):
            print("Error: Please provide a valid PDF file path (must end with .pdf).")
        else:
            return pdf_path

def main():
    # Get user input for PDF path
    pdf_path = get_valid_pdf_path()

    # Get base name without extension, e.g., "book" from "book.pdf"
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Define base directory (same as main.py)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Define working directory based on PDF name
    working_dir = os.path.join(base_dir, base_name)
    os.makedirs(working_dir, exist_ok=True)

    # Define subdirectories
    standardized_dir = os.path.join(working_dir, "standardized_text")
    text_parts_dir = os.path.join(working_dir, "text_parts")
    audio_parts_dir = os.path.join(working_dir, "audio_parts")
    output_dir = os.path.join(working_dir, "output")

    # Create all directories
    for d in [standardized_dir, text_parts_dir, audio_parts_dir, output_dir]:
        os.makedirs(d, exist_ok=True)

    # Define output paths
    standardized_path = os.path.join(standardized_dir, "standardized.txt")
    final_audio_path = os.path.join(output_dir, "final_output.mp3")

    # Step 1: Process PDF
    process_pdf(pdf_path, standardized_path)
    print(f"✅ Standardized text saved to: {standardized_path}")

    # Step 2: Split text
    process_text(standardized_path, text_parts_dir)
    print(f"✅ Text parts saved to: {text_parts_dir}")

    # Step 3: Convert to audio with threading
    process_text_to_audio(text_parts_dir, audio_parts_dir, num_threads=2)
    print(f"✅ Audio parts saved to: {audio_parts_dir}")

    # Step 4: Merge audio
    merge_audio(audio_parts_dir, final_audio_path)
    print(f"✅ Final audio saved to: {final_audio_path}")

if __name__ == "__main__":
    main()
