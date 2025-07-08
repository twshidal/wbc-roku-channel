from jinja2 import Environment, FileSystemLoader
import json
import os
import shutil

# File paths
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "static_site"
JSON_FILE = "WorthBC.json"
STATIC_SRC = "static"
STATIC_DEST = os.path.join(OUTPUT_DIR, "static")

# Ensure output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the template
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template("index_static.html")

# Load JSON data
with open(JSON_FILE, encoding="utf-8") as f:
    data = json.load(f)

# Define a fake url_for for compatibility (optional here)
def fake_url_for(endpoint, filename=None):
    if endpoint == 'static' and filename:
        return f'static/{filename}'
    return '#'

print(f"type(data): {type(data)}")
print(f"type(data['items']): {type(data.get('items'))}")
print(f"data['items'] sample: {data.get('items')[:2] if isinstance(data.get('items'), list) else 'Not a list'}")


# Render the template
rendered_html = template.render(data=data, url_for=fake_url_for)

# Write the rendered HTML to output directory
output_path = os.path.join(OUTPUT_DIR, "index.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(rendered_html)

print(f"✅ Static HTML generated at {output_path}")

# Copy static assets to output folder
if os.path.exists(STATIC_DEST):
    shutil.rmtree(STATIC_DEST)  # Remove old static folder

shutil.copytree(STATIC_SRC, STATIC_DEST)

print(f"✅ Static assets copied to {STATIC_DEST}")
