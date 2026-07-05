from models.gemma_model import ask_gemma_text, ask_gemma_visual
from extractor.load_files import extract_text
from tree_generator import generate_mindmap_structure
from graph_builder import build_mindmap_graph, display_mindmap

# text = ask_gemma_text("What is machine learning")
# visual = ask_gemma_visual("img.jpg", "Describe this image??")

# extracted_text = extract_text("img.jpg")

def generate_mindmap(file_path):
    print("Extracting text...")
    text = extract_text(file_path)
    print(f"Extracted {len(text)} characters.")

    print("Generating mind map structure...")
    tree = generate_mindmap_structure(text)

    print("Building interactive visualization...")
    html_file = build_mindmap_graph(tree)

    return tree, html_file

tree, html_file = generate_mindmap("img.jpg")
print(display_mindmap(html_file))
# python demo.py