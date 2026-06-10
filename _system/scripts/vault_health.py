import os
import sys
import argparse
from datetime import datetime
import utils

VAULT_DIR = "/Users/kira/Documents/Brains/Knowledge"

DECAY_EXEMPT = ["pillar", "decision", "playbook"]
DECAY_FAST = ["fact", "source"]
BASE_DECAY_RATE = 0.04
FAST_DECAY_RATE = 0.08

def get_months_elapsed(verified_at_str):
    if not verified_at_str:
        return 0.0
    try:
        # standard ISO 8601 YYYY-MM-DD
        vdate = datetime.strptime(verified_at_str[:10], "%Y-%m-%d")
        cdate = datetime.now()
        delta = cdate - vdate
        return max(0.0, delta.days / 30.4375)
    except Exception:
        return 0.0

def run_health(auto=False):
    print("Running Vault Health Audit...")
    
    # 1. Load all nodes
    nodes = utils.get_all_nodes(VAULT_DIR)
    
    # Pre-map edges to detect orphans
    # Maps node_id/path to list of inbound nodes
    inbound_edges = {}
    outbound_count = {}
    
    # We will identify nodes by both their short ID (e.g. "attention-mechanism") and their full path relative to vault (e.g. "concept/attention-mechanism")
    node_by_id = {}
    node_by_relpath = {}
    
    for file_path, fm, body in nodes:
        nid = fm.get("id")
        ntype = fm.get("node_type")
        relpath = f"{ntype}/{nid}"
        
        node_by_id[nid] = (file_path, fm, body)
        node_by_relpath[relpath] = (file_path, fm, body)
        
        inbound_edges[relpath] = []
        inbound_edges[nid] = []
        outbound_count[relpath] = 0
        
    # Build edge adjacency lists
    contradict_edges = []
    
    for file_path, fm, body in nodes:
        nid = fm.get("id")
        ntype = fm.get("node_type")
        source_relpath = f"{ntype}/{nid}"
        
        edges = fm.get("edges", [])
        outbound_count[source_relpath] = len(edges)
        
        for edge in edges:
            target = edge.get("target", "")
            etype = edge.get("type", "")
            # target can be e.g. "concept/attention-mechanism" or "attention-mechanism"
            if target:
                if target in inbound_edges:
                    inbound_edges[target].append(source_relpath)
                # handle if target is concept/attention-mechanism but stored by short ID
                target_short = target.split('/')[-1]
                if target_short in inbound_edges:
                    inbound_edges[target_short].append(source_relpath)
            
            if etype == "contradicts":
                contradict_edges.append((source_relpath, target, edge.get("note", "")))

    # 2. Process confidence decay and flag issues
    decay_proposals = []
    below_threshold_nodes = []
    stale_nodes = []
    orphan_nodes = []
    
    nodes_by_type_stats = {t: {"count": 0, "below_threshold": 0, "stale": 0} for t in utils.NODE_TYPES}
    
    for file_path, fm, body in nodes:
        nid = fm.get("id")
        ntype = fm.get("node_type")
        relpath = f"{ntype}/{nid}"
        
        nodes_by_type_stats[ntype]["count"] += 1
        
        # Stale check
        verified_at = fm.get("verified_at", "")
        months = get_months_elapsed(verified_at)
        if months >= 3.0:
            stale_nodes.append((relpath, fm.get("title", ""), verified_at))
            nodes_by_type_stats[ntype]["stale"] += 1
            
        # Decay calculation
        conf = fm.get("confidence", 0.0)
        volatility = fm.get("volatility", "stable")
        
        rate = 0.0
        if ntype in DECAY_EXEMPT:
            rate = 0.0
        elif ntype in DECAY_FAST or volatility == "volatile":
            rate = FAST_DECAY_RATE
        else:
            rate = BASE_DECAY_RATE
            
        new_conf = conf
        if rate > 0.0 and months > 0.0:
            decay_amount = rate * months
            new_conf = max(0.0, round(conf - decay_amount, 3))
            
        if new_conf < conf:
            decay_proposals.append((file_path, fm, body, conf, new_conf, months))
            
        # Below threshold check
        final_conf = new_conf if auto else conf
        if final_conf < 0.3:
            below_threshold_nodes.append((relpath, fm.get("title", ""), final_conf))
            nodes_by_type_stats[ntype]["below_threshold"] += 1
            
        # Orphan check
        # An orphan has no outbound edges and no inbound edges
        out_cnt = outbound_count.get(relpath, 0)
        in_cnt = len(inbound_edges.get(relpath, [])) + len(inbound_edges.get(nid, []))
        if out_cnt == 0 and in_cnt == 0:
            orphan_nodes.append((relpath, fm.get("title", "")))

    # 3. Handle contradictions registration
    registered_contradictions = 0
    for src, tgt, note in contradict_edges:
        # Normalize and ensure contradiction registered
        # target might be short or full relpath
        src_clean = src
        tgt_clean = tgt
        if '/' not in tgt_clean:
            # find full path
            full_t = utils.get_node_path(VAULT_DIR, tgt_clean)
            if full_t:
                # relative path
                parts = full_t.replace(VAULT_DIR + "/", "").replace(".md", "").split('/')
                if len(parts) >= 2:
                    tgt_clean = f"{parts[-2]}/{parts[-1]}"
                    
        # Add to register
        utils.add_contradiction(VAULT_DIR, src_clean, tgt_clean, note if note else "Contradiction edge in graph.")
        registered_contradictions += 1

    # 4. Perform updates
    updates_applied = 0
    if decay_proposals:
        print(f"\nFound {len(decay_proposals)} nodes eligible for confidence decay:")
        for file_path, fm, body, old_conf, new_conf, months in decay_proposals:
            print(f"  - {fm.get('node_type')}/{fm.get('id')} : {old_conf} -> {new_conf} ({months:.1f} months elapsed)")
            
        apply_decay = False
        if auto:
            apply_decay = True
        else:
            response = input("\nApply these confidence decay updates to the node files? [y/N]: ").strip().lower()
            if response in ['y', 'yes']:
                apply_decay = True
                
        if apply_decay:
            for file_path, fm, body, old_conf, new_conf, months in decay_proposals:
                fm["confidence"] = new_conf
                utils.write_node(file_path, fm, body)
                updates_applied += 1
            print(f"Applied confidence decay to {updates_applied} nodes.")
        else:
            print("Confidence decay updates skipped.")
            
    # 5. Read open contradictions count from file
    open_contr_count = 0
    contr_path = os.path.join(VAULT_DIR, "_system", "CONTRADICTIONS.md")
    if os.path.isfile(contr_path):
        with open(contr_path, 'r', encoding='utf-8') as f:
            contr_content = f.read()
        open_contr_count = len(re.findall(r"Status:\s*open", contr_content, re.IGNORECASE))

    # 6. Generate HEALTH-REPORT.md
    report_path = os.path.join(VAULT_DIR, "_system", "HEALTH-REPORT.md")
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_lines = [
        "# Vault Health Report",
        "",
        f"> Generated by `/vault-health` — do not edit manually.",
        f"> Last run: {today}",
        "",
        "---",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total nodes | {len(nodes)} |",
        f"| Orphan nodes | {len(orphan_nodes)} |",
        f"| Open contradictions | {open_contr_count} |",
        f"| Stale nodes (> 3 months) | {len(stale_nodes)} |",
        f"| Low-confidence nodes (< 0.3) | {len(below_threshold_nodes)} |",
        "",
        "---",
        "",
        "## Nodes by Type",
        "",
        "| Type | Count | Below Threshold (< 0.3) | Stale (> 3 months) |",
        "|------|-------|--------------------------|---------------------|"
    ]
    
    for t in utils.NODE_TYPES:
        stats = nodes_by_type_stats[t]
        report_lines.append(f"| {t} | {stats['count']} | {stats['below_threshold']} | {stats['stale']} |")
        
    report_lines.extend([
        "",
        "---",
        "",
        "## Nodes Flagged for Review (Confidence < 0.3)",
        ""
    ])
    
    if not below_threshold_nodes:
        report_lines.append("_No low-confidence nodes detected._")
    else:
        for relpath, title, conf in below_threshold_nodes:
            report_lines.append(f"- [[{relpath}|{title}]] (conf: {conf})")
            
    report_lines.extend([
        "",
        "---",
        "",
        "## Stale Nodes (verified_at > 3 months ago)",
        ""
    ])
    
    if not stale_nodes:
        report_lines.append("_No stale nodes detected._")
    else:
        for relpath, title, verified_at in stale_nodes:
            report_lines.append(f"- [[{relpath}|{title}]] (last verified: {verified_at})")
            
    report_lines.extend([
        "",
        "---",
        "",
        "## Orphan Nodes (No connections)",
        ""
    ])
    
    if not orphan_nodes:
        report_lines.append("_No orphan nodes detected._")
    else:
        for relpath, title in orphan_nodes:
            report_lines.append(f"- [[{relpath}|{title}]]")
            
    report_lines.extend([
        "",
        "---",
        "",
        "## Recommended Actions",
        ""
    ])
    
    actions = []
    if below_threshold_nodes:
        actions.append("- Re-verify or archive the low-confidence nodes listed above.")
    if stale_nodes:
        actions.append("- Conduct a review of stale nodes to update their details and refresh `verified_at` dates.")
    if orphan_nodes:
        actions.append("- Link orphan nodes to related concepts, or delete them if no longer relevant.")
    if open_contr_count > 0:
        actions.append("- Investigate and resolve the active contradictions registered in `CONTRADICTIONS.md`.")
    if not actions:
        actions.append("- None! The vault is in excellent health.")
        
    report_lines.extend(actions)
    report_lines.append("")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report_lines))
        
    # 7. Log to LOG.md
    log_details = [
        f"Scan complete: {len(nodes)} nodes audited",
        f"Confidence decay applied to {updates_applied} nodes",
        f"Detected {len(orphan_nodes)} orphans and {len(stale_nodes)} stale nodes",
        f"Health report updated at `_system/HEALTH-REPORT.md`"
    ]
    utils.log_operation(VAULT_DIR, "vault-health", f"Vault Health Audit", "auto" if auto else "interactive", log_details)
    print("\nVault health check completed successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit knowledge graph health.")
    parser.add_argument("--auto", action="store_true", help="Apply decay silently without prompting.")
    args = parser.parse_args()
    
    run_health(auto=args.auto)
