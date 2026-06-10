import os
import re
from datetime import datetime

NODE_TYPES = [
    "pillar", "decision", "concept", "question", "playbook", "task",
    "event", "pattern", "hypothesis", "fact", "source", "bookmark",
    "note", "contact", "reference", "custom"
]

def parse_val(val_str):
    val_str = val_str.strip()
    if not val_str:
        return ""
    if val_str.startswith('"') and val_str.endswith('"'):
        return val_str[1:-1].replace('\\"', '"')
    if val_str.startswith("'") and val_str.endswith("'"):
        return val_str[1:-1]
    if val_str == "true":
        return True
    if val_str == "false":
        return False
    if val_str == "[]":
        return []
    if val_str.startswith('[') and val_str.endswith(']'):
        inner = val_str[1:-1].strip()
        if not inner:
            return []
        items = []
        # simple split by comma, ignoring commas inside quotes
        parts = re.split(r',\s*(?=(?:[^"]*"[^"]*")*[^"]*$)', inner)
        for x in parts:
            items.append(parse_val(x.strip()))
        return items
    try:
        if '.' in val_str:
            return float(val_str)
        return int(val_str)
    except ValueError:
        return val_str

def parse_frontmatter(content):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None, content
    fm_text = match.group(1)
    body = content[match.end():]
    
    fm = {}
    lines = fm_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.strip().startswith('#'):
            i += 1
            continue
        parts = line.split(':', 1)
        if len(parts) == 2:
            key = parts[0].strip()
            val_str = parts[1].strip()
            # Check if this is the start of a block list (e.g. edges or list of items)
            if val_str == "" and i + 1 < len(lines) and (lines[i+1].strip().startswith('-') or lines[i+1].startswith('  ')):
                items = []
                i += 1
                list_lines = []
                while i < len(lines) and (lines[i].startswith('  ') or lines[i].startswith('\t') or not lines[i].strip() or lines[i].strip().startswith('-')):
                    if lines[i].strip() and not lines[i].startswith(' ') and not lines[i].startswith('\t') and not lines[i].strip().startswith('-'):
                        break
                    list_lines.append(lines[i])
                    i += 1
                i -= 1
                
                current_dict = None
                for l in list_lines:
                    l_strip = l.strip()
                    if not l_strip or l_strip.startswith('#'):
                        continue
                    if l_strip.startswith('-'):
                        item_val = l_strip[1:].strip()
                        is_key_value = bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_-]*\s*:(?:\s|$)', item_val))
                        if is_key_value:
                            current_dict = {}
                            items.append(current_dict)
                            s_parts = item_val.split(':', 1)
                            current_dict[s_parts[0].strip()] = parse_val(s_parts[1].strip())
                        elif item_val == "":
                            current_dict = {}
                            items.append(current_dict)
                        else:
                            current_dict = None
                            items.append(parse_val(item_val))
                    else:
                        if current_dict is not None:
                            s_parts = l_strip.split(':', 1)
                            if len(s_parts) == 2:
                                current_dict[s_parts[0].strip()] = parse_val(s_parts[1].strip())
                fm[key] = items
            else:
                fm[key] = parse_val(val_str)
        i += 1
    return fm, body

def dump_frontmatter(fm):
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            if not v:
                lines.append(f"{k}: []")
            elif all(isinstance(x, (str, int, float, bool)) for x in v):
                lines.append(f"{k}:")
                for item in v:
                    if isinstance(item, str):
                        lines.append(f"  - \"{item}\"")
                    else:
                        lines.append(f"  - {str(item).lower() if isinstance(item, bool) else item}")
            else:
                lines.append(f"{k}:")
                for item in v:
                    lines.append("  - type: \"" + item.get("type", "") + "\"")
                    lines.append("    target: \"" + item.get("target", "") + "\"")
                    lines.append("    weight: " + str(item.get("weight", 0.5)))
                    lines.append("    note: \"" + item.get("note", "").replace('"', '\\"') + "\"")
        elif isinstance(v, bool):
            lines.append(f"{k}: {str(v).lower()}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        else:
            # string
            lines.append(f"{k}: \"{str(v).replace('\"', '\\\"')}\"")
    lines.append("---")
    return "\n".join(lines)

def read_node(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return parse_frontmatter(content)

def write_node(path, fm, body):
    fm_str = dump_frontmatter(fm)
    content = fm_str + "\n" + body.lstrip()
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_all_nodes(vault_path):
    nodes = []
    for t in NODE_TYPES:
        dir_path = os.path.join(vault_path, t)
        if not os.path.isdir(dir_path):
            continue
        for filename in os.listdir(dir_path):
            if filename.endswith(".md"):
                file_path = os.path.join(dir_path, filename)
                try:
                    fm, body = read_node(file_path)
                    if fm:
                        nodes.append((file_path, fm, body))
                except Exception as e:
                    # Silently skip corrupted nodes or log them
                    pass
    return nodes

def get_node_path(vault_path, node_id):
    # node_id might be "concept/attention-mechanism" or just "attention-mechanism"
    if '/' in node_id:
        # Full relative path check
        full_path = os.path.join(vault_path, node_id + ".md")
        if os.path.isfile(full_path):
            return full_path
    else:
        # Scan all folders
        for t in NODE_TYPES:
            full_path = os.path.join(vault_path, t, node_id + ".md")
            if os.path.isfile(full_path):
                return full_path
    return None

def update_index(vault_path):
    nodes_by_type = {t: [] for t in NODE_TYPES}
    total_count = 0
    for file_path, fm, body in get_all_nodes(vault_path):
        ntype = fm.get("node_type")
        if ntype in nodes_by_type:
            nodes_by_type[ntype].append((fm.get("id"), fm.get("title", ""), fm.get("summary", ""), fm.get("confidence", 0.0)))
            total_count += 1
            
    index_path = os.path.join(vault_path, "_system", "INDEX.md")
    today = datetime.now().strftime("%Y-%m-%d")
    
    lines = [
        "# Knowledge Graph Index",
        "",
        f"> Last updated: {today}",
        f"> Total nodes: {total_count}",
        "",
        "---",
        ""
    ]
    
    # Map type to heading title
    headings = {
        "pillar": "Pillars",
        "decision": "Decisions",
        "concept": "Concepts",
        "question": "Questions",
        "playbook": "Playbooks",
        "task": "Tasks",
        "event": "Events",
        "pattern": "Patterns",
        "hypothesis": "Hypotheses",
        "fact": "Facts",
        "source": "Sources",
        "bookmark": "Bookmarks",
        "note": "Notes",
        "contact": "Contacts",
        "reference": "References",
        "custom": "Custom"
    }
    
    for t in NODE_TYPES:
        lines.append(f"## {headings.get(t, t.capitalize())}")
        nodes = nodes_by_type[t]
        if not nodes:
            lines.append("_No nodes yet._")
        else:
            # Sort by ID or title
            nodes.sort(key=lambda x: x[0])
            for nid, title, summary, conf in nodes:
                lines.append(f"- [[{t}/{nid}|{title}]] `{t}` — {summary} (conf: {conf})")
        lines.append("")
        
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))

def log_operation(vault_path, op_name, subject, mode, details_list):
    log_path = os.path.join(vault_path, "_system", "LOG.md")
    today = datetime.now().strftime("%Y-%m-%d")
    
    new_entry = [
        f"## [{today}] {op_name} | \"{subject}\" | mode={mode}"
    ]
    for d in details_list:
        new_entry.append(f"- {d}")
    new_entry.append("")
    
    # Read existing log
    log_content = ""
    if os.path.isfile(log_path):
        with open(log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
            
    # Insert new entry in reverse-chronological order after the header
    header_marker = "---\n"
    idx = log_content.find(header_marker)
    if idx != -1:
        header = log_content[:idx + len(header_marker)]
        rest = log_content[idx + len(header_marker):]
        updated_content = header + "\n" + "\n".join(new_entry) + rest
    else:
        updated_content = "# Operation Log\n\nAll vault operations are recorded here in reverse-chronological order (newest first).\n\n**Format**: `## [YYYY-MM-DD] <operation> | \"<subject>\" | mode=<mode>`\n\n---\n\n" + "\n".join(new_entry)
        
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

def add_contradiction(vault_path, node_a, node_b, conflict_desc, detected_by="agent"):
    contr_path = os.path.join(vault_path, "_system", "CONTRADICTIONS.md")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Read existing contradictions
    content = ""
    if os.path.isfile(contr_path):
        with open(contr_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
    # Parse existing contradiction IDs to avoid duplication
    # Check if contradiction between A and B already exists
    # Normalize order of node_a and node_b to check
    a_normalized = min(node_a, node_b)
    b_normalized = max(node_a, node_b)
    
    # Simple check for existing entry
    search_str_1 = f"[[{a_normalized}]] ↔ [[{b_normalized}]]"
    search_str_2 = f"[[{b_normalized}]] ↔ [[{a_normalized}]]"
    
    if search_str_1 in content or search_str_2 in content:
        # Already registered
        return
        
    # Build new entry
    new_entry = [
        f"### [{today}] {a_normalized} ↔ {b_normalized} — Status: open",
        "",
        f"- **Node A**: [[{a_normalized}]]",
        f"- **Node B**: [[{b_normalized}]]",
        f"- **Conflict**: {conflict_desc}",
        f"- **Detected by**: {detected_by}",
        f"- **Status**: open",
        f"- **Resolution**: _(empty until resolved)_",
        ""
    ]
    
    header_marker = "## Active Contradictions\n"
    idx = content.find(header_marker)
    if idx != -1:
        before = content[:idx + len(header_marker)]
        after = content[idx + len(header_marker):]
        # Check if there was a "_No contradictions registered yet._" placeholder
        placeholder = "_No contradictions registered yet._"
        if placeholder in after:
            after = after.replace(placeholder, "")
        updated_content = before + "\n" + "\n".join(new_entry) + after.lstrip()
    else:
        # Fallback if file format is unexpected
        updated_content = content + "\n\n" + "\n".join(new_entry)
        
    with open(contr_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
