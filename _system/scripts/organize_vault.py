import os
import sys
import utils

VAULT_DIR = "/Users/kira/Documents/Brains/Knowledge"

def audit_vault():
    print("Auditing vault structure...")
    nodes = utils.get_all_nodes(VAULT_DIR)
    
    orphans = []
    mismatches = []
    broken_edges = []
    weak_edges = []
    stale_nodes = []
    
    # Pre-map node IDs and relpaths
    node_ids = set()
    node_relpaths = set()
    inbound = {}
    outbound = {}
    
    for file_path, fm, body in nodes:
        nid = fm.get("id")
        ntype = fm.get("node_type")
        relpath = f"{ntype}/{nid}"
        
        node_ids.add(nid)
        node_relpaths.add(relpath)
        inbound[relpath] = []
        inbound[nid] = []
        outbound[relpath] = []

    # Parse edges
    for file_path, fm, body in nodes:
        nid = fm.get("id")
        ntype = fm.get("node_type")
        relpath = f"{ntype}/{nid}"
        
        edges = fm.get("edges", [])
        for edge in edges:
            target = edge.get("target", "")
            etype = edge.get("type", "")
            
            if not target:
                continue
                
            outbound[relpath].append(target)
            
            # Record inbound edge
            if target in inbound:
                inbound[target].append(relpath)
            # handle target represented by short ID
            target_short = target.split('/')[-1]
            if target_short in inbound:
                inbound[target_short].append(relpath)
                
            # Weak edge check
            if etype == "related_to":
                weak_edges.append((relpath, target))
                
            # Broken edge check
            # Verify if target exists as a file
            target_resolved = utils.get_node_path(VAULT_DIR, target)
            if not target_resolved:
                broken_edges.append((relpath, target, file_path, fm, body))

    # Audit each node
    for file_path, fm, body in nodes:
        nid = fm.get("id")
        ntype = fm.get("node_type")
        relpath = f"{ntype}/{nid}"
        
        # 1. Type mismatch check: does file folder match node_type?
        folder = os.path.basename(os.path.dirname(file_path))
        if folder != ntype:
            mismatches.append((file_path, folder, ntype, fm, body))
            
        # 2. Orphan check
        out_cnt = len(outbound.get(relpath, []))
        in_cnt = len(inbound.get(relpath, [])) + len(inbound.get(nid, []))
        if out_cnt == 0 and in_cnt == 0:
            orphans.append((relpath, fm.get("title", "")))
            
        # 3. Stale check
        verified_at = fm.get("verified_at", "")
        months = utils.get_months_elapsed(verified_at) if hasattr(utils, "get_months_elapsed") else 0.0
        # If months not defined in utils, calculate here
        if not verified_at:
            months = 0.0
        else:
            try:
                from datetime import datetime
                vdate = datetime.strptime(verified_at[:10], "%Y-%m-%d")
                delta = datetime.now() - vdate
                months = delta.days / 30.4375
            except Exception:
                months = 0.0
                
        if months >= 3.0:
            stale_nodes.append((relpath, verified_at))

    # Present findings
    print("\n=== STRUCTURAL AUDIT RESULTS ===")
    
    # Mismatches
    print(f"\n[1] Node Type Mismatches: {len(mismatches)}")
    for file_path, folder, ntype, fm, body in mismatches:
        print(f"  - File is in folder '{folder}/' but frontmatter node_type is '{ntype}'")
        print(f"    Path: {file_path}")
        
    # Orphans
    print(f"\n[2] Orphan Nodes (no connections): {len(orphans)}")
    for relpath, title in orphans:
        print(f"  - [[{relpath}]] : \"{title}\"")
        
    # Broken edges
    print(f"\n[3] Broken Edges (targets do not exist): {len(broken_edges)}")
    for source_relpath, target, file_path, fm, body in broken_edges:
        print(f"  - [[{source_relpath}]] contains edge to missing target: '{target}'")
        
    # Weak edges
    print(f"\n[4] Weak Edges ('related_to' fallbacks): {len(weak_edges)}")
    for relpath, target in weak_edges[:10]:
        print(f"  - [[{relpath}]] ↔ {target}")
    if len(weak_edges) > 10:
        print(f"  ... and {len(weak_edges) - 10} more weak edges")
        
    # Stale nodes
    print(f"\n[5] Stale Nodes (> 3 months since verified): {len(stale_nodes)}")
    for relpath, verified_at in stale_nodes:
        print(f"  - [[{relpath}]] : last verified on {verified_at}")
        
    # Interactive Resolutions
    print("\n=== PROPOSED RESOLUTIONS ===")
    actions_taken = []
    
    # Fix mismatches (move files)
    if mismatches:
        response = input(f"\nDo you want to fix folder mismatches by moving files to correct folders? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            for file_path, folder, ntype, fm, body in mismatches:
                nid = fm.get("id")
                new_dir = os.path.join(VAULT_DIR, ntype)
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                new_path = os.path.join(new_dir, f"{nid}.md")
                try:
                    os.rename(file_path, new_path)
                    print(f"  Moved: {folder}/{nid}.md -> {ntype}/{nid}.md")
                    actions_taken.append(f"Moved {nid} from {folder}/ to {ntype}/")
                except Exception as e:
                    print(f"  Error moving {nid}: {e}")
                    
    # Fix broken edges by removing them
    if broken_edges:
        response = input(f"\nDo you want to remove broken edges? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            for source_relpath, target, file_path, fm, body in broken_edges:
                edges = fm.get("edges", [])
                new_edges = [edge for edge in edges if edge.get("target") != target]
                fm["edges"] = new_edges
                utils.write_node(file_path, fm, body)
                print(f"  Removed edge to '{target}' in [[{source_relpath}]]")
                actions_taken.append(f"Removed broken edge {source_relpath} -> {target}")

    if actions_taken:
        # Rebuild index and log operation
        utils.update_index(VAULT_DIR)
        utils.log_operation(VAULT_DIR, "organize-vault", "Vault Organization", "interactive", actions_taken)
        print("\nVault organized, index rebuilt, and actions logged.")
    else:
        print("\nNo changes applied.")

if __name__ == "__main__":
    audit_vault()
