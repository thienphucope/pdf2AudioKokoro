import os
import subprocess
import re

def get_number(filename):
    """Extracts part and segment numbers from filename for sorting."""
    numbers = re.findall(r'\d+', filename)
    if len(numbers) >= 2:
        return (int(numbers[0]), int(numbers[1]))  # (part_number, segment_number)
    elif numbers:
        return (int(numbers[0]), 0)  # Only part_number, assume segment 0
    return (float('inf'), float('inf'))  # No numbers, push to end

def merge_audio(input_dir, output_path):
    """Merges audio files into one using ffmpeg with relative paths."""
    audio_files = sorted(
        [f for f in os.listdir(input_dir) if f.endswith((".wav", ".mp3"))],
        key=get_number
    )
    if not audio_files:
        raise ValueError("No audio files found in the input directory.")

    # Print the order of files being merged
    print("Merging files in the following order:")
    for i, file in enumerate(audio_files, 1):
        print(f"{i}. {file}")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Create file_list.txt in the input_dir
    list_file = os.path.join(input_dir, "file_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for file in audio_files:
            # Use relative path (just the filename) since file_list.txt is in input_dir
            f.write(f"file '{file}'\n")

    # FFmpeg command: concatenate and encode to MP3
    command = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-acodec", "mp3",  # Explicitly encode to MP3
        "-ab", "192k",     # Bitrate 192 kbps (adjustable)
        output_path
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"✅ Successfully merged audio into: {output_path}")
    except subprocess.CalledProcessError as e:
        print("❌ FFmpeg error:", e)
        print("🔧 FFmpeg command was:", " ".join(command))
        raise
    finally:
        # Clean up temporary file
        if os.path.exists(list_file):
            os.remove(list_file)

if __name__ == "__main__":
    # Example usage with relative paths
    input_dir = "audio_parts"
    output_path = "output/final_output.mp3"
    merge_audio(input_dir, output_path)