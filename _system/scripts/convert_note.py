import os
import sys
import re
import json
import argparse
import urllib.request
from datetime import datetime
import utils

VAULT_DIR = "/Users/kira/Documents/Brains/Knowledge"

DECOMPOSITION_PROMPT = """You are a Knowledge Graph Architect.
Your task is to analyze the following source text and decompose it into a set of atomic, typed knowledge graph nodes.

Each node must match one of these 16 types:
{node_types}

Rules:
1. Atomicity: One core concept, choice, fact, playbook, event, or note per file. Typically 50-300 lines of body content.
2. Edge Creation: Edges should connect the new nodes to each other and to existing concepts. Edge types are:
   - supports, contradicts, depends_on, derived_from, related_to, part_of, preceded_by, followed_by, authored_by, tagged_with
3. Every node MUST have a 'derived_from' edge pointing to the source node that represents this raw material.
4. Output must be a valid JSON list of node objects. No other text.

JSON format expected:
[
  {{
    "id": "kebab-case-id",
    "title": "Node Title",
    "node_type": "concept",
    "summary": "One-line description of the node",
    "confidence": 0.85,
    "volatility": "stable",
    "visibility": "public",
    "edges": [
      {{
        "type": "derived_from",
        "target": "source/{source_id}",
        "weight": 1.0,
        "note": "Derived from source material"
      }}
    ],
    "body": "## Summary\\n...\\n## Content\\n..."
  }}
]

Source Text:
---
{source_text}
---
"""

def get_available_model():
    try:
        url = "http://localhost:11434/api/tags"
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = [m["name"] for m in data.get("models", [])]
            # Prefer instruct or chat models
            for m in ["qwen2.5:14b-instruct", "qwen3.5:397b-cloud", "gpt-oss:20b"]:
                if m in models:
                    return m
            if models:
                return models[0]
    except Exception:
        pass
    return None

def decompose_with_llm(text, source_id, model):
    node_types_str = ", ".join(utils.NODE_TYPES)
    prompt = DECOMPOSITION_PROMPT.format(
        node_types=node_types_str,
        source_id=source_id,
        source_text=text
    )
    
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        print(f"Contacting local Ollama (model: {model}) for node decomposition...")
        with urllib.request.urlopen(req, timeout=90) as response:
            res = json.loads(response.read().decode('utf-8'))
            resp_text = res.get("response", "")
            return json.loads(resp_text)
    except Exception as e:
        print(f"Ollama decomposition failed: {e}")
        return None

def fallback_decomposition(text, source_id):
    print("Ollama not available or failed. Running rule-based fallback decomposition...")
    # Fallback splits note by H2 headers or just creates a single note/concept node
    lines = text.split('\n')
    title = "Extracted Note"
    for line in lines:
        if line.startswith('# '):
            title = line[2:].strip()
            break
            
    summary = text[:100].replace('\n', ' ') + "..."
    clean_title = re.sub(r'[^\w\s-]', '', title)
    node_id = clean_title.lower().replace(' ', '-')
    if not node_id:
        node_id = "extracted-note-" + datetime.now().strftime("%H%M%S")
        
    # Create single node
    node = {
        "id": node_id,
        "title": title,
        "node_type": "concept",
        "summary": summary,
        "confidence": 0.7,
        "volatility": "stable",
        "visibility": "public",
        "edges": [
            {
                "type": "derived_from",
                "target": f"source/{source_id}",
                "weight": 1.0,
                "note": "Derived from source notes"
            }
        ],
        "body": f"## Summary\n{summary}\n\n## Content\n{text}"
    }
    return [node]

def process_ingest(source_path, mode="supervised", json_payload_path=None):
    # 1. Read note content
    source_title = os.path.basename(source_path)
    if os.path.isfile(source_path):
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        # treat source_path as raw text directly
        content = source_path
        source_title = "Pasted Raw Text"
        
    source_id = re.sub(r'[^\w\s-]', '', os.path.splitext(source_title)[0]).lower().replace(' ', '-')
    if not source_id:
        source_id = "raw-source-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        
    # 2. Get decomposition plan
    nodes_to_create = None
    if json_payload_path and os.path.isfile(json_payload_path):
        try:
            with open(json_payload_path, 'r', encoding='utf-8') as f:
                nodes_to_create = json.load(f)
            print("Loaded pre-computed decomposition plan from JSON payload.")
        except Exception as e:
            print(f"Error reading JSON payload: {e}")
            
    if not nodes_to_create:
        model = get_available_model()
        if model:
            nodes_to_create = decompose_with_llm(content, source_id, model)
        if not nodes_to_create:
            nodes_to_create = fallback_decomposition(content, source_id)

    # 3. Supervised confirmation
    if mode == "supervised":
        print("\n=== Proposed Node Decomposition ===")
        for i, node in enumerate(nodes_to_create, 1):
            print(f"[{i}] Type: {node.get('node_type')} | ID: {node.get('id')} | Title: \"{node.get('title')}\"")
            print(f"    Summary: {node.get('summary')}")
            edges = node.get("edges", [])
            for e in edges:
                print(f"    Edge: -> {e.get('target')} ({e.get('type')})")
            print()
            
        confirm = input("Approve this decomposition plan? [y/N]: ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Operation aborted by user.")
            sys.exit(0)

    # 4. Create the source node representing the raw material
    today = datetime.now().strftime("%Y-%m-%d")
    source_node_fm = {
        "id": source_id,
        "title": source_title,
        "node_type": "source",
        "summary": f"Raw source material processed on {today}.",
        "status": "active",
        "confidence": 0.9,
        "created_at": today,
        "verified_at": today,
        "verified_by": "auto",
        "volatility": "stable",
        "visibility": "public",
        "source_refs": [source_path] if os.path.isfile(source_path) else [],
        "edges": []
    }
    
    # Write source node
    source_node_body = f"# {source_title}\n\n## Content\n\n```markdown\n{content}\n```\n"
    source_file_path = os.path.join(VAULT_DIR, "source", f"{source_id}.md")
    utils.write_node(source_file_path, source_node_fm, source_node_body)
    print(f"Created source node: source/{source_id}.md")

    # 5. Create each proposed node
    created_list = []
    contradictions_flagged = []
    
    for node in nodes_to_create:
        nid = node.get("id")
        ntype = node.get("node_type")
        if ntype not in utils.NODE_TYPES:
            ntype = "concept"
            
        fm = {
            "id": nid,
            "title": node.get("title", ""),
            "node_type": ntype,
            "summary": node.get("summary", ""),
            "status": "active",
            "confidence": node.get("confidence", 0.8),
            "created_at": today,
            "verified_at": today,
            "verified_by": "agent" if mode != "supervised" else "human",
            "volatility": node.get("volatility", "stable"),
            "visibility": node.get("visibility", "public"),
            "derived_from": [f"source/{source_id}"],
            "edges": node.get("edges", [])
        }
        
        # Ensure derived_from edge is present
        has_derived = False
        for e in fm["edges"]:
            if e.get("type") == "derived_from" and e.get("target") == f"source/{source_id}":
                has_derived = True
            if e.get("type") == "contradicts":
                # register contradiction
                target = e.get("target")
                note = e.get("note", "Contradiction detected during ingestion.")
                utils.add_contradiction(VAULT_DIR, f"{ntype}/{nid}", target, note)
                contradictions_flagged.append(f"{ntype}/{nid} ↔ {target}")
                
        if not has_derived:
            fm["edges"].append({
                "type": "derived_from",
                "target": f"source/{source_id}",
                "weight": 1.0,
                "note": "Derived from source"
            })
            
        file_path = os.path.join(VAULT_DIR, ntype, f"{nid}.md")
        utils.write_node(file_path, fm, node.get("body", ""))
        created_list.append(f"{ntype}/{nid}")
        print(f"Created node: {ntype}/{nid}.md")

    # 6. Post-creation house keeping
    # Rebuild Index
    utils.update_index(VAULT_DIR)
    
    # Move source to processed folder
    if os.path.isfile(source_path):
        processed_dir = os.path.join(VAULT_DIR, "raw", "processed")
        if not os.path.exists(processed_dir):
            os.makedirs(processed_dir)
        dest = os.path.join(processed_dir, source_title)
        os.rename(source_path, dest)
        print(f"Moved raw file to raw/processed/{source_title}")

    # Log Operation
    log_details = [
        f"Ingested source: \"{source_title}\"",
        f"Created nodes: {', '.join(created_list)}",
        f"Contradictions registered: {', '.join(contradictions_flagged) if contradictions_flagged else 'None'}",
        f"Ingestion mode: {mode}"
    ]
    utils.log_operation(VAULT_DIR, "convert-note", f"Ingest: {source_title}", mode, log_details)
    print("\nIngestion completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest raw notes into knowledge graph nodes.")
    parser.add_argument("source", type=str, help="Path to raw note or text to ingest.")
    parser.add_argument("--mode", type=str, choices=["supervised", "hybrid", "autonomous"], default="supervised",
                        help="Ingestion mode (supervised | hybrid | autonomous).")
    parser.add_argument("--json-payload", type=str, default=None,
                        help="Optional path to a pre-computed node decomposition JSON payload.")
    args = parser.parse_args()
    
    process_ingest(args.source, args.mode, args.json_payload)
