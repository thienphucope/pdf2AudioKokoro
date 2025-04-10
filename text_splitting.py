import os
import re

def split_text(text, max_length=1000):
    """Splits text into parts based on a maximum length."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    parts = []
    current_part = ""

    for sentence in sentences:
        if len(current_part) + len(sentence) <= max_length:
            current_part += sentence + " "
        else:
            parts.append(current_part.strip())
            current_part = sentence + " "
    if current_part:
        parts.append(current_part.strip())
    
    return parts

def save_text_parts(parts, output_dir):
    """Saves text parts to individual files."""
    os.makedirs(output_dir, exist_ok=True)
    for i, part in enumerate(parts):
        output_path = os.path.join(output_dir, f"part_{i}.txt")
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(part)

def process_text(input_path, output_dir):
    """Reads text, splits it, and saves the parts."""
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()
    parts = split_text(text)
    save_text_parts(parts, output_dir)
    return parts