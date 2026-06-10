import os
import sys

VAULT_DIR = "/Users/kira/Documents/Brains/Knowledge"
NODE_TYPES = [
    "pillar", "decision", "concept", "question", "playbook", "task",
    "event", "pattern", "hypothesis", "fact", "source", "bookmark",
    "note", "contact", "reference", "custom"
]
RAW_SUBDIRS = ["articles", "papers", "transcripts", "images", "processed", "assets"]

def init_vault():
    print(f"Initializing Knowledge Graph Vault at {VAULT_DIR}...")
    
    # 1. Create 16 node directories
    for t in NODE_TYPES:
        path = os.path.join(VAULT_DIR, t)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"  Created directory: {t}/")
            
    # 2. Create raw/ subdirectories
    for r in RAW_SUBDIRS:
        path = os.path.join(VAULT_DIR, "raw", r)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"  Created directory: raw/{r}/")
            
    # 3. Create agent skills directories
    for s in [".claude/skills", ".gemini/skills"]:
        path = os.path.join(VAULT_DIR, s)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"  Created directory: {s}/")
            
    # 4. Create _system/ scripts and templates directories
    for d in ["_system/scripts", "_system/templates"]:
        path = os.path.join(VAULT_DIR, d)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"  Created directory: {d}/")
            
    print("Vault directories initialized successfully.")

if __name__ == "__main__":
    init_vault()
