import json
import re
from models.gemma_model import ask_gemma_text

MINDMAP_PROMPT_TEMPLATE = """You are a mind map generator.
Read the following content and organize it into a hierarchical mind map.

Return ONLY valid JSON in this exact format, nothing else:
{{
  "title": "Central Topic",
  "children": [
    {{
      "title": "Main Branch 1",
      "children": [
        {{"title": "Sub-point 1.1", "children": []}},
        {{"title": "Sub-point 1.2", "children": []}}
      ]
    }},
    {{
      "title": "Main Branch 2",
      "children": []
    }}
  ]
}}

Rules:
- 3 to 6 main branches max
- 2 to 4 sub-points per branch
- Keep titles short (3-8 words)
- No text outside the JSON
- No markdown code fences

Content:
{content}
"""

def clean_json_output(raw_text):
    """Strip markdown fences and extra text, isolate JSON object."""
    text = raw_text.strip()
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text

def generate_mindmap_structure(text, max_retries=3):
    """Ask the model to convert text into a tree JSON, with retry on bad JSON."""
    # Truncate very long text to keep prompt manageable
    trimmed = text[:6000]
    prompt = MINDMAP_PROMPT_TEMPLATE.format(content=trimmed)

    for attempt in range(max_retries):
        raw = ask_gemma_text(prompt, max_tokens=1024)
        cleaned = clean_json_output(raw)
        try:
            tree = json.loads(cleaned)
            return tree
        except json.JSONDecodeError:
            print(f"Attempt {attempt+1}: invalid JSON, retrying...")
            continue

    raise ValueError("Model failed to produce valid JSON after retries.")