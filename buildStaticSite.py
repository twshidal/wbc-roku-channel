from jinja2 import Environment, FileSystemLoader
import json
import os

# File paths
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "docs"  # Changed from static_site to docs
JSON_FILE = "WorthBC.json"

# Ensure output folder exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load the template
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
template = env.get_template("index_static.html")  # Using static template

# Load JSON data
with open(JSON_FILE) as f:
    data = json.load(f)

# Define a fake url_for function for static path references
def fake_url_for(endpoint, filename=None):
    if endpoint == 'static' and filename:
        return f'static/{filename}'
    elif endpoint == 'run_script':
        return '#run-script-disabled'
    return '#'

# Render the template
rendered_html = template.render(data=data, url_for=fake_url_for)

# Write the rendered HTML to output directory
output_path = os.path.join(OUTPUT_DIR, "index.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(rendered_html)

print(f"✅ Static HTML generated at {output_path}")
