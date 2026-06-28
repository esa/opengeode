#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import markdown
from pygments.formatters import HtmlFormatter

# ----------------- CONFIGURATION -----------------
WIKI_DIR = "wiki"
OUTPUT_DIR = "html_output"

FILES_TO_PROCESS = [
    'Detailed_SDL_tutorial.md', 
    'Technical_topic_OpenGEODE_SDL_Operators_How_to_work_with_data.md'
]
# -------------------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

html_files = []
image_files = []

# 1. Regex to catch complex nested linked images: [![Alt](img_path)](link_path)
LINKED_IMAGE_REGEX = re.compile(r'\[\!\[(.*?)\]\((.*?)\)\]\((.*?)\)', re.DOTALL)
# 2. Regex to catch standalone images: ![Alt](img_path)
STANDALONE_IMAGE_REGEX = re.compile(r'\!\[(.*?)\]\((.*?)\)', re.DOTALL)

# Generate dark-themed styling rules for code blocks
CSS_STYLE_BLOCK = HtmlFormatter(style="tango").get_style_defs('.codehilite')

def find_file_case_insensitive(directory, target_rel_path):
    """
    Search for an asset within common folders ignoring case sensitivity.
    Returns the real path if found, otherwise None.
    """
    # Safely unpack and strip parameters out of URL/path fragments
    clean_rel = target_rel_path.split('?')[0].split('#')[0].split()[0].strip('"\'')
    base_name = os.path.basename(clean_rel)
    
    # Define possible relative directories to scan
    possible_dirs = [
        directory,
        os.path.join(directory, "img"),
        os.path.join(directory, "uploads"),
        os.path.dirname(os.path.join(directory, clean_rel))
    ]
    
    for d in possible_dirs:
        if not os.path.exists(d):
            continue
        # Scan files in directory case-insensitively
        for entry in os.listdir(d):
            if entry.lower() == base_name.lower():
                full_path = os.path.join(d, entry)
                if os.path.isfile(full_path):
                    return full_path
    return None

print(f"--- Starting targeted media asset extraction for: {FILES_TO_PROCESS} ---")

for target_file in FILES_TO_PROCESS:
    source_path = os.path.join(WIKI_DIR, target_file)
    
    if not os.path.exists(source_path):
        print(f"[ERROR] The file {source_path} does not exist. Skipping.")
        continue

    with open(source_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # --- Phase A: Handle Linked Images Block Wrapper ---
    # Finds strings like [![Opengeode overview](img/700px-Og-complete.png)](img/Og-complete.png)
    linked_matches = LINKED_IMAGE_REGEX.findall(md_content)
    for alt_text, img_path, link_path in linked_matches:
        # Look up the thumbnail file first, fall back to the main linked image file
        resolved_path = find_file_case_insensitive(WIKI_DIR, img_path)
        if not resolved_path:
            resolved_path = find_file_case_insensitive(WIKI_DIR, link_path)
            
        if resolved_path:
            flat_name = os.path.basename(resolved_path)
            dest_path = os.path.normpath(os.path.join(OUTPUT_DIR, flat_name))
            shutil.copy2(resolved_path, dest_path)
            
            if flat_name not in image_files:
                image_files.append(flat_name)
                print(f" -> Copied nested asset: {flat_name}")
            
            # Use safe regex replacement to overwrite the complex link layout with a clean asset block
            escaped_img = re.escape(img_path)
            escaped_link = re.escape(link_path)
            escaped_alt = re.escape(alt_text)
            
            # This handles tiny syntax differences or whitespace variances inside the original markdown tags
            pattern = rf'\[\!\[{escaped_alt}\]\s*\({escaped_img}\)\s*\]\s*\({escaped_link}(?:\s+"[^"]*")?\)'
            clean_alt_text = alt_text.replace('\n', ' ').replace('\r', '')
            clean_md_tag = f'<img src="{flat_name}" alt="{clean_alt_text}" />'
            md_content = re.sub(pattern, clean_md_tag, md_content, flags=re.IGNORECASE)
        else:
            print(f" [WARNING] Could not locate file for linked image: {img_path} or {link_path}")

    # --- Phase B: Handle Standalone Images ---
    standalone_matches = STANDALONE_IMAGE_REGEX.findall(md_content)
    for alt_text, img_path in standalone_matches:
        resolved_path = find_file_case_insensitive(WIKI_DIR, img_path)
        if resolved_path:
            flat_name = os.path.basename(resolved_path)
            dest_path = os.path.normpath(os.path.join(OUTPUT_DIR, flat_name))
            shutil.copy2(resolved_path, dest_path)
            
            if flat_name not in image_files:
                image_files.append(flat_name)
                print(f" -> Copied standalone asset: {flat_name}")
                
            # Replace image reference path safely with flattened name using regex
            escaped_img = re.escape(img_path)
            escaped_alt = re.escape(alt_text)
            pattern = rf'\!\[{escaped_alt}\]\s*\({escaped_img}\)'
            clean_alt_text = alt_text.replace('\n', ' ').replace('\r', '')
            md_content = re.sub(pattern, f'<img src="{flat_name}" alt="{clean_alt_text}" />', md_content, flags=re.IGNORECASE)
        else:
            print(f" [WARNING] Could not locate file for standalone image: {img_path}")

    # Render Markdown safely into pristine HTML
    html_content = markdown.markdown(
        md_content, 
        extensions=['toc', 'tables', 'fenced_code', 'codehilite']
    )
    
    # Modern clean styling injection layer
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{target_file.replace('.md', '').replace('_', ' ')}</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; padding: 25px; color: #222; max-width: 900px; margin: 0 auto; }}
        pre {{ background-color: #f6f8fa; border: 1px solid #e1e4e8; padding: 15px; border-radius: 6px; overflow-x: auto; margin: 15px 0; }}
        code {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 14px; background-color: rgba(27,31,35,0.05); padding: 0.2em 0.4em; border-radius: 3px; }}
        pre code {{ background-color: transparent; padding: 0; border: 0; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #f7f7f7; font-weight: bold; }}
        img {{ max-width: 100%; height: auto; display: block; margin: 20px 0; border: 1px solid #eee; border-radius: 4px; }}
        {CSS_STYLE_BLOCK}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    # Final HTML generation
    target_html_name = f"{target_file.rsplit('.', 1)[0]}.html"
    dest_html_path = os.path.join(OUTPUT_DIR, target_html_name)
    
    with open(dest_html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
        
    html_files.append(target_html_name)
    print(f"[OK] Clean HTML output generated: {target_html_name}\n")


# 4. Generate the 'opengeode.qhp' file
index_page = html_files[0] if html_files else "index.html"

qhp_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<QtHelpProject version="1.0">
    <namespace>esa.int.taste.opengeode</namespace>
    <virtualFolder>doc</virtualFolder>
    <customFilter name="OpenGEODE 3.9">
        <filterAttribute>opengeode</filterAttribute>
        <filterAttribute>3.9</filterAttribute>
    </customFilter>
    <filterSection>
        <filterAttribute>opengeode</filterAttribute>
        <filterAttribute>3.9</filterAttribute>
        <toc>
"""

keywords_content = "        <keywords>\n"

for target_file in FILES_TO_PROCESS:
    target_html_name = f"{target_file.rsplit('.', 1)[0]}.html"
    source_path = os.path.join(WIKI_DIR, target_file)
    if not os.path.exists(source_path): continue
    with open(source_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    title = target_html_name.replace('.html', '').replace('Technical_topic_', '').replace('OpenGEODE_', '').replace('_', ' ')
    if 'Detailed SDL tutorial' in title: title = 'SDL Tutorial'
    if 'SDL Operators How to work with data' in title: title = 'How to work with data'

    qhp_content += f'            <section title="{title.replace('\"', '&quot;').replace('&', '&amp;')}" ref="{target_html_name}">\n'
    
    pattern = re.compile(r'<a name="([^"]+)"></a>\n(#+)\s+(.*)')
    matches = pattern.findall(md_content)
    
    stack = [1]
    
    for anchor, hashes, text in matches:
        if text.lower() == 'contents' or text.lower() == 'index':
            continue
            
        level = len(hashes) + 1
        
        while len(stack) > 1 and level <= stack[-1]:
            qhp_content += "    " * stack[-1] + '            </section>\n'
            stack.pop()
            
        qhp_content += "    " * level + f'            <section title="{text.replace('\"', '&quot;').replace('&', '&amp;')}" ref="{target_html_name}#{anchor}">\n'
        stack.append(level)
        
        keywords_content += f'            <keyword name="{text.replace('\"', '&quot;').replace('&', '&amp;')}" id="{anchor}" ref="{target_html_name}#{anchor}"/>\n'
        
    while len(stack) > 1:
        qhp_content += "    " * stack[-1] + '            </section>\n'
        stack.pop()
        
    qhp_content += f'            </section>\n'

qhp_content += """        </toc>\n"""
keywords_content += """        </keywords>\n"""
qhp_content += keywords_content

qhp_content += """        <files>
"""

for html in html_files:
    qhp_content += f'            <file>{html}</file>\n'
for img in image_files:
    qhp_content += f'            <file>{img}</file>\n'

qhp_content += """        </files>
    </filterSection>
</QtHelpProject>
"""

with open(os.path.join(OUTPUT_DIR, "opengeode.qhp"), "w", encoding="utf-8") as f:
    f.write(qhp_content)


# 5. Generate the 'opengeode.qhcp' file
qhcp_content = """<?xml version="1.0" encoding="utf-8" ?>
<QHelpCollectionProject version="1.0">
    <docFiles>
        <generate>
            <file>
                <input>opengeode.qhp</input>
                <output>opengeode.qch</output>
            </file>
        </generate>
        <register>
            <file>opengeode.qch</file>
        </register>
    </docFiles>
</QHelpCollectionProject>
"""

with open(os.path.join(OUTPUT_DIR, "opengeode.qhcp"), "w", encoding="utf-8") as f:
    f.write(qhcp_content)


# 6. Automatic Compilation using spacecreator.AppImage
print("--- Launching QHelp compilation via spacecreator.AppImage ---")
try:
    subprocess.run(
        ["spacecreator.AppImage", "--qhelpgenerator", "-o", "opengeode.qch", "opengeode.qhp"],
        cwd=OUTPUT_DIR, check=True
    )
    subprocess.run(
        ["spacecreator.AppImage", "--qhelpgenerator", "-o", "opengeode.qhc", "opengeode.qhcp"],
        cwd=OUTPUT_DIR, check=True
    )
    print("\n[SUCCESS] Pipeline complete. Code highlighting and all image wrappers are fixed!")
except Exception as e:
    print(f"\n[ERROR] Compilation failed: {e}")

