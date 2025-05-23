import os
import re
import threading
from queue import Queue
import soundfile as sf
from kokoro import KPipeline  # External TTS library
import warnings
from huggingface_hub import login  # Add this import

# Retrieve Hugging Face token from environment variable and log in
HF_TOKEN = os.environ.get("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable not set. Please set it with your Hugging Face token.")
print(f"DEBUG: HF_TOKEN = {HF_TOKEN}")
login(token=HF_TOKEN)  # Explicitly log in to Hugging Face

# Tắt cảnh báo liên quan đến dropout trong RNN
warnings.filterwarnings("ignore", message="dropout option adds dropout after all but last recurrent layer")
# Tắt cảnh báo về weight_norm bị deprecated
warnings.filterwarnings("ignore", message="`torch.nn.utils.weight_norm` is deprecated")

def get_number(filename):
    """Extracts number from filename for sorting."""
    numbers = re.findall(r'\d+', filename)
    return int(numbers[0]) if numbers else float('inf')

def generate_audio(pipeline, text, voice, speed, output_path):
    """Generates audio for a text block and saves all segments."""
    generator = pipeline(text, voice=voice, speed=speed, split_pattern=r'\n+')
    audio_files = []
    for i, (gs, ps, audio) in enumerate(generator):
        audio_file = f"{os.path.splitext(output_path)[0]}_{i}.wav"
        sf.write(audio_file, audio, 24000)
        audio_files.append(audio_file)
        print("Generated audio segment:", audio_file)
    return audio_files

def worker(queue, pipeline_config):
    """Worker function for threading."""
    pipeline = KPipeline(lang_code=pipeline_config['lang_code'])
    while True:
        try:
            task = queue.get_nowait()
        except Queue.Empty:
            break
        text, output_path = task
        generate_audio(pipeline, text, pipeline_config['voice'], pipeline_config['speed'], output_path)
        queue.task_done()

def process_text_to_audio(input_dir, output_dir, num_threads=2):
    """Processes text files into audio using multiple threads, with resume and recheck last part."""
    os.makedirs(output_dir, exist_ok=True)

    txt_files = sorted(
        [f for f in os.listdir(input_dir) if f.endswith('.txt')],
        key=get_number
    )

    audio_files = [f for f in os.listdir(output_dir) if f.endswith('.wav')]

    existing_prefixes = set()
    prefix_to_parts = {}

    for f in audio_files:
        match = re.match(r'^(part_\d+)_\d+\.wav$', f)
        if match:
            prefix = match.group(1)
            existing_prefixes.add(prefix)
            prefix_to_parts.setdefault(prefix, 0)
            prefix_to_parts[prefix] += 1

    if prefix_to_parts:
        last_prefix = sorted(prefix_to_parts.keys(), key=get_number)[-1]
        print(f"⚠️ Detected incomplete or last audio segment for {last_prefix}. Will re-process it.")
        existing_prefixes.remove(last_prefix)
    else:
        last_prefix = None

    queue = Queue()
    pipeline_config = {'lang_code': 'a', 'voice': 'af_heart', 'speed': 1}

    tasks_added = 0
    for txt_file in txt_files:
        output_base = os.path.splitext(txt_file)[0]
        if output_base in existing_prefixes:
            print(f"✅ Skipping {txt_file}: All audio segments seem completed.")
            continue

        txt_path = os.path.join(input_dir, txt_file)
        output_path = os.path.join(output_dir, txt_file.replace('.txt', '.wav'))
        with open(txt_path, 'r', encoding='utf-8') as file:
            text = file.read()
        queue.put((text, output_path))
        tasks_added += 1

    if tasks_added == 0:
        print("🎉 No new or incomplete text files to process. All done!")
        return

    threads = []
    for _ in range(min(num_threads, tasks_added)):
        thread = threading.Thread(target=worker, args=(queue, pipeline_config))
        thread.start()
        threads.append(thread)

    queue.join()
    for thread in threads:
        thread.join()
    print(f"✅ Processed {tasks_added} new or incomplete text files into audio.")