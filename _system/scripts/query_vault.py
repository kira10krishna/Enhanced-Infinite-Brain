import os
import sys
import re
import argparse
import utils

VAULT_DIR = "/Users/kira/Documents/Brains/Knowledge"

# Compiled regex patterns for speed optimization
RE_CLEAN_QUERY = re.compile(r'[^\w\s-]')
RE_INDEX_ENTRY = re.compile(r'^-\s*\[\[([^/|\]]+)/([^|\]]+)(?:\|([^\]]+))?\]\]\s*`?(\w+)`?\s*—\s*(.*?)\s*\(conf:\s*([0-9.]+)\)$')

STOPWORDS = {
    "what", "is", "how", "why", "the", "a", "an", "and", "or", "but", "in", "on", "at", 
    "to", "for", "with", "about", "against", "between", "into", "through", "during", 
    "before", "after", "above", "below", "from", "up", "down", "of", "off", "over", 
    "under", "again", "further", "then", "once", "here", "there", "when", "where", 
    "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", 
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", 
    "can", "will", "just", "don", "should", "now", "i", "me", "my", "myself", "we", 
    "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", 
    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", 
    "itself", "they", "them", "their", "theirs", "themselves"
}

def extract_keywords(query):
    query_clean = RE_CLEAN_QUERY.sub(' ', query.lower())
    words = query_clean.split()
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 1]
    keywords = list(dict.fromkeys(keywords))
    return keywords if keywords else list(dict.fromkeys(words))

def score_node(fm, keywords):
    nid = fm.get("id", "").lower()
    title = fm.get("title", "").lower()
    summary = fm.get("summary", "").lower()
    tags = [t.lower() for t in fm.get("tags", []) if isinstance(t, str)]
    confidence = fm.get("confidence", 0.0)
    
    score = 0.0
    for kw in keywords:
        if kw in title:
            score += 3.0
            if title.startswith(kw):
                score += 1.0
        if kw in nid:
            score += 2.0
        if tags:
            score += sum(1.5 for tag in tags if kw in tag)
        if kw in summary:
            score += 1.0
            
    return score * (0.5 + confidence * 0.5)

def run_query(query, limit=5):
    print(f"Query: \"{query}\"\n")
    keywords = extract_keywords(query)
    print(f"Keywords: {', '.join(keywords)}\n")
    
    # 1. Attempt to load nodes from INDEX.md to avoid scanning disk (algorithmic optimization)
    index_path = os.path.join(VAULT_DIR, "_system", "INDEX.md")
    index_nodes = []
    
    if os.path.isfile(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            for line in f:
                m = RE_INDEX_ENTRY.match(line.strip())
                if m:
                    ntype, nid, title, _, summary, conf = m.groups()
                    fm = {
                        "id": nid,
                        "title": title if title else nid,
                        "node_type": ntype,
                        "summary": summary,
                        "confidence": float(conf),
                        "tags": []
                    }
                    index_nodes.append(fm)
                    
    # 2. Score candidate nodes
    seeds = []
    if index_nodes:
        scored_index_nodes = []
        for fm in index_nodes:
            score = score_node(fm, keywords)
            if score > 0.0:
                scored_index_nodes.append((score, fm))
        scored_index_nodes.sort(key=lambda x: x[0], reverse=True)
        
        # Load details from disk ONLY for the top seed candidates
        for score, fm in scored_index_nodes[:3]:
            nid = fm["id"]
            path = utils.get_node_path(VAULT_DIR, nid)
            if path:
                try:
                    actual_fm, body = utils.read_node(path)
                    seeds.append((score, path, actual_fm, body))
                except Exception:
                    pass
    else:
        # Fallback to loading all nodes from disk if INDEX.md is missing/empty
        print("Warning: INDEX.md is empty or missing. Falling back to disk scan...")
        nodes = utils.get_all_nodes(VAULT_DIR)
        
        # Pre-populate get_node_path cache
        for file_path, fm, body in nodes:
            nid = fm.get("id")
            ntype = fm.get("node_type")
            utils._node_path_cache[(VAULT_DIR, nid)] = file_path
            utils._node_path_cache[(VAULT_DIR, f"{ntype}/{nid}")] = file_path
            
        scored_nodes = []
        for file_path, fm, body in nodes:
            score = score_node(fm, keywords)
            if score > 0.0:
                scored_nodes.append((score, file_path, fm, body))
        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        seeds = scored_nodes[:3]

    if not seeds:
        print("No matching candidate nodes found.")
        return

    # 3. Traverse edges from seeds to find supporting context (1 hop)
    traversed_relpaths = set()
    traversed_nodes = []
    
    for score, file_path, fm, body in seeds:
        nid = fm.get("id")
        ntype = fm.get("node_type")
        relpath = f"{ntype}/{nid}"
        
        if relpath not in traversed_relpaths:
            traversed_relpaths.add(relpath)
            traversed_nodes.append((score + 5.0, file_path, fm, body, "seed"))
            
        edges = fm.get("edges", [])
        for edge in edges:
            target = edge.get("target", "")
            etype = edge.get("type", "")
            if not target:
                continue
                
            target_relpath = target
            if '/' not in target_relpath:
                tpath = utils.get_node_path(VAULT_DIR, target_relpath)
                if tpath:
                    target_relpath = tpath.replace(VAULT_DIR + "/", "").replace(".md", "")
                    
            if target_relpath not in traversed_relpaths:
                tpath = utils.get_node_path(VAULT_DIR, target_relpath)
                if tpath:
                    try:
                        t_fm, t_body = utils.read_node(tpath)
                        t_score = score_node(t_fm, keywords)
                        edge_weight = edge.get("weight", 0.5)
                        combined_score = (score * edge_weight) + t_score
                        
                        traversed_relpaths.add(target_relpath)
                        traversed_nodes.append((combined_score, tpath, t_fm, t_body, f"edge ({etype} from {relpath})"))
                    except Exception:
                        pass

    # 4. Pillar Auto-Injection from index references
    for fm in index_nodes if index_nodes else []:
        if fm.get("node_type") == "pillar":
            nid = fm.get("id")
            relpath = f"pillar/{nid}"
            if relpath not in traversed_relpaths:
                p_score = score_node(fm, keywords)
                if p_score > 0.0 or any(kw in nid for kw in keywords):
                    tpath = utils.get_node_path(VAULT_DIR, nid)
                    if tpath:
                        try:
                            p_fm, p_body = utils.read_node(tpath)
                            traversed_relpaths.add(relpath)
                            traversed_nodes.append((p_score + 10.0, tpath, p_fm, p_body, "pillar_injection"))
                        except Exception:
                            pass

    # Sort traversed context by score descending
    traversed_nodes.sort(key=lambda x: x[0], reverse=True)
    final_context_nodes = traversed_nodes[:limit]
    
    # 5. Output formatted context block
    print(f"=== RETRIEVED CONTEXT (Top {len(final_context_nodes)} nodes) ===\n")
    
    for i, (score, file_path, fm, body, reason) in enumerate(final_context_nodes, 1):
        nid = fm.get("id")
        ntype = fm.get("node_type")
        title = fm.get("title", "")
        summary = fm.get("summary", "")
        conf = fm.get("confidence", 0.0)
        ver_at = fm.get("verified_at", "")
        derived = fm.get("derived_from", [])
        
        print(f"[{i}] Node: {ntype}/{nid} (Title: \"{title}\")")
        print(f"    Confidence: {conf} | Verified At: {ver_at}")
        print(f"    Reason for selection: {reason} (Score: {score:.2f})")
        print(f"    Summary: {summary}")
        if derived:
            print(f"    Derived From: {', '.join(derived)}")
            
        print("\n--- BODY CONTENT ---")
        print(body.strip())
        print("---------------------\n")
        
    print("=== SYNTHESIS INSTRUCTIONS ===")
    print("Please synthesize an answer to the query using ONLY the retrieved context above.")
    print("For every claim made, append a lineage citation in this exact format:")
    print("`Based on [[type/node-id]] (confidence: C, derived from [[source/citation-source]], verified YYYY-MM-DD)`")
    
    # Log the query operation
    log_details = [
        f"Query: \"{query}\"",
        f"Keywords extracted: {keywords}",
        f"Retrieved {len(final_context_nodes)} nodes for context"
    ]
    utils.log_operation(VAULT_DIR, "query-vault", f"Query: {query[:30]}...", "auto", log_details)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query the knowledge graph for context.")
    parser.add_argument("query", type=str, help="The search query or question.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of context nodes to retrieve.")
    args = parser.parse_args()
    
    run_query(args.query, args.limit)
