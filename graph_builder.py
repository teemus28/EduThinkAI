from pyvis.network import Network
from IPython.display import IFrame
import uuid
from IPython.display import HTML
import base64
import os

import os
import uuid
from pyvis.network import Network

def build_mindmap_graph(
    tree,
    output_file=None,
    return_html=False
):
    net = Network(
        height="700px",
        width="100%",
        bgcolor="#ffffff",      # white background
        font_color="#1a1a1a",   # dark text for readability
        directed=False,
        cdn_resources="remote"
    )

    net.barnes_hut()

    # Palette tuned for light background — muted, professional tones
    colors = [
        "#4A90D9",  # blue
        "#E85D5D",  # red
        "#3DBFA6",  # teal
        "#9B6BC9",  # purple
        "#F0A93A",  # orange
        "#5B9BD5",  # light blue
    ]

    def add_nodes(node, parent_id=None, depth=0):
        node_id = str(uuid.uuid4())

        size = max(35 - depth * 8, 12)
        color = colors[depth % len(colors)]

        net.add_node(
            node_id,
            label=node["title"],
            size=size,
            shape="box",              # rectangular nodes, like your reference
            color={
                "background": color,
                "border": "#333333",
                "highlight": {"background": color, "border": "#000000"}
            },
            font={"color": "#ffffff" if depth < 2 else "#1a1a1a", "size": 14},
            borderWidth=1
        )

        if parent_id:
            net.add_edge(
                parent_id,
                node_id,
                color="#888888",   # soft gray edges instead of harsh lines
                width=1.5
            )

        for child in node.get("children", []):
            add_nodes(child, node_id, depth + 1)

    add_nodes(tree)

    # Optional physics controls — comment out for a cleaner production UI
    # net.show_buttons(filter_=["physics"])

    # Better default layout for readability
    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 150,
          "springConstant": 0.04
        },
        "minVelocity": 0.75
      }
    }
    """)

    if return_html:
        return net.generate_html()

    if output_file is None:
        output_file = "mindmap.html"

    net.write_html(output_file)

    return output_file




# def build_mindmap_graph(
#     tree,
#     output_file=None,
#     return_html=False
# ):
#     net = Network(
#         height="700px",
#         width="100%",
#         bgcolor="#000000",
#         font_color="white",
#         directed=False,
#         cdn_resources="remote"
#     )

#     net.barnes_hut()

#     def add_nodes(node, parent_id=None, depth=0):
#         node_id = str(uuid.uuid4())

#         size = max(35 - depth * 8, 12)
#         colors = [
#             "#ff6b6b",
#             "#4ecdc4",
#             "#ffe66d",
#             "#a29bfe"
#         ]

#         net.add_node(
#             node_id,
#             label=node["title"],
#             size=size,
#             color=colors[depth % len(colors)]
#         )

#         if parent_id:
#             net.add_edge(parent_id, node_id)

#         for child in node.get("children", []):
#             add_nodes(child, node_id, depth + 1)

#     add_nodes(tree)

#     net.show_buttons(filter_=["physics"])

#     # Return HTML directly
#     if return_html:
#         return net.generate_html()

#     # Save to file
#     if output_file is None:
#         output_file = "mindmap.html"

#     net.write_html(output_file)

#     return output_file
# def build_mindmap_graph(tree, output_dir="outputs", output_file="mindmap.html"):
#     os.makedirs(output_dir, exist_ok=True)

#     filename = f"{uuid.uuid4()}.html"

#     output_path = os.path.join(
#         output_dir,
#         filename
#     )
#     net = Network(height="700px", width="100%", bgcolor="#111111", font_color="white", directed=False)
#     net.barnes_hut()

#     def add_nodes(node, parent_id=None, depth=0):
#         node_id = str(uuid.uuid4())
#         size = max(35 - depth * 8, 12)
#         color = ["#ff6b6b", "#4ecdc4", "#ffe66d", "#a29bfe"][depth % 4]
#         net.add_node(node_id, label=node["title"], size=size, color=color)
#         if parent_id:
#             net.add_edge(parent_id, node_id)
#         for child in node.get("children", []):
#             add_nodes(child, node_id, depth + 1)

#     add_nodes(tree)
#     net.show_buttons(filter_=['physics'])
#     net.write_html(output_file)
#     return output_file





def display_mindmap(html_file, height=750):
    """Display a pyvis-generated HTML file inline in Colab (no localhost needed)."""
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    # Embed directly using srcdoc — avoids Colab's iframe-to-localhost issue
    iframe_html = f"""
    <iframe srcdoc="{html_content.replace('"', '&quot;')}" 
            width="100%" height="{height}" 
            style="border:none;">
    </iframe>
    """
    return HTML(iframe_html)

