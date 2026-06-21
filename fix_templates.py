import re

def fix_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix broken tags (remove internal newlines within {{ ... }})
    # This regex finds {{ and everything until }} and replaces internal newlines with space
    new_content = re.sub(r'\{\{(.*?)\}\}', lambda m: '{{ ' + m.group(1).replace('\n', ' ').strip() + ' }}', content, flags=re.DOTALL)
    
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

import os

def get_all_templates(directory):
    templates = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".html"):
                templates.append(os.path.join(root, file))
    return templates

files = get_all_templates(r'c:\Users\USER\actividad 6to\gestion_escolar\templates')

for f in files:
    try:
        fix_file(f)
        print(f"Fixed {f}")
    except Exception as e:
        print(f"Error fixing {f}: {e}")
