import os
import json
import re
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY is missing! Run: export GEMINI_API_KEY='your_key_here'")
    exit(1)

client = genai.Client(api_key=api_key)

file_path = "songs_977_cleaned.js"
try:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_content = f.read()
except FileNotFoundError:
    print(f"Error: Could not find {file_path} in current folder!")
    exit(1)

start_idx = raw_content.find("[")
end_idx = raw_content.rfind("]") + 1
json_str = raw_content[start_idx:end_idx]

json_str = re.sub(r'\\(?![/"bfnrtu])', r'\\\\', json_str)

try:
    songs_data = json.loads(json_str)
except Exception as e:
    json_str = json_str.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
    songs_data = json.loads(json_str)

prompt_template = """
You are an expert hymnal editor. Fix the errors in this JSON list of songs.

RULES:
1. Fix OCR broken words (e.g., "\\ndown" -> " down", "\\ns" -> "s ").
2. Fix broken song titles where text spilled into lyrics (e.g. Title "ZION", Lyrics "S HILL" -> Title "ZION'S HILL").
3. Fix capitalization and punctuation.
4. Spacing rules for lyrics:
   - Separate lines with 1 newline: \\n
   - Separate stanzas with 2 newlines: \\n\\n
   - Separate verse before going into Chorus/Refrain with 3 newlines: \\n\\n\\n

Return ONLY valid JSON matching the exact schema provided.
"""

cleaned_songs = []
BATCH_SIZE = 10

print(f"Total songs loaded successfully: {len(songs_data)}")

for i in range(0, len(songs_data), BATCH_SIZE):
    batch = songs_data[i:i + BATCH_SIZE]
    print(f"Processing songs {i + 1} to {min(i + BATCH_SIZE, len(songs_data))}...")
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt_template, json.dumps(batch)],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
            ),
        )
        cleaned_batch = json.loads(response.text)
        cleaned_songs.extend(cleaned_batch)
    except Exception as e:
        print(f"Error on batch starting at {i}: {e}")
        cleaned_songs.extend(batch)

output_content = f"const songs = {json.dumps(cleaned_songs, indent=2)};\n\nexport default songs;"
with open("songs_977_fixed.js", "w", encoding="utf-8") as f:
    f.write(output_content)

print("Done! Saved cleaned output to songs_977_fixed.js")
