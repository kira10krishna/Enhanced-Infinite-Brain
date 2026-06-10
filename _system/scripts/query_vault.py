import os
import sys
import re
import argparse
import utils

VAULT_DIR = "/Users/kira/Documents/Brains/Knowledge"

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
    query_clean = re.sub(r'[^\w\s-]', ' ', query.lower())
    words = query_clean.split()
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 1]
    return keywords if keywords else words

def score_node(fm, keywords):
    score = 0.0
    nid = fm.get("id", "").lower()
    title = fm.get("title", "").lower()
    summary = fm.get("summary", "").lower()
    tags = [t.lower() for t in fm.get("tags", []) if isinstance(t, str)]
    
    for kw in keywords:
        # Title match (highest weight)
        if kw in title:
            score += 3.0
            if title.startswith(kw):
                score += 1.0
        # ID match
        if kw in nid:
            score += 2.0
        # Tags match
        for tag in tags:
            if kw in tag:
                score += 1.5
        # Summary match
        if kw in summary:
            score += 1.0
            
    # Apply confidence scaling (higher confidence nodes are preferred)
    score *= (0.5 + fm.get("confidence", 0.0) * 0.5)
    return score

def run_query(query, limit=5):
    print(f"Query: \"{query}\"\n")
    keywords = extract_keywords(query)
    print(f"Keywords: {', '.join(keywords)}\n")
    
    # 1. Load all nodes
    nodes = utils.get_all_nodes(VAULT_DIR)
    if not nodes:
        print("The vault is empty. No nodes found to query.")
        return
        
    # Map nodes by relpath and short ID
    node_map = {}
    relpath_map = {}
    for file_path, fm, body in nodes:
        nid = fm.get("id")
        ntype = fm.get("node_type")
        relpath = f"{ntype}/{nid}"
        node_map[nid] = (file_path, fm, body)
        relpath_map[relpath] = (file_path, fm, body)

    # 2. Score all nodes
    scored_nodes = []
    for file_path, fm, body in nodes:
        score = score_node(fm, keywords)
        if score > 0.0:
            scored_nodes.append((score, file_path, fm, body))
            
    # Sort by score descending
    scored_nodes.sort(key=lambda x: x[0], reverse=True)
    
    # If no keywords matched, take nodes with highest confidence or recent updates
    if not scored_nodes:
        print("No direct keyword matches found. Showing highest-confidence nodes.")
        for file_path, fm, body in nodes[:limit]:
            scored_nodes.append((0.0, file_path, fm, body))
            
    # 3. Identify seed candidate nodes
    seeds = scored_nodes[:3] # Top 3 seeds
    
    # 4. Traverse edges from seeds to find supporting context (1 hop)
    traversed_relpaths = set()
    traversed_nodes = []
    
    for score, file_path, fm, body in seeds:
        nid = fm.get("id")
        ntype = fm.get("node_type")
        relpath = f"{ntype}/{nid}"
        
        if relpath not in traversed_relpaths:
            traversed_relpaths.add(relpath)
            traversed_nodes.append((score + 5.0, file_path, fm, body, "seed")) # Add seed bump
            
        # Traverse edges
        edges = fm.get("edges", [])
        for edge in edges:
            target = edge.get("target", "")
            etype = edge.get("type", "")
            if not target:
                continue
                
            # Resolve target relpath
            target_relpath = target
            if '/' not in target_relpath:
                # Resolve short ID
                tpath = utils.get_node_path(VAULT_DIR, target_relpath)
                if tpath:
                    target_relpath = tpath.replace(VAULT_DIR + "/", "").replace(".md", "")
                    
            if target_relpath in relpath_map and target_relpath not in traversed_relpaths:
                t_file, t_fm, t_body = relpath_map[target_relpath]
                # Score target node
                t_score = score_node(t_fm, keywords)
                edge_weight = edge.get("weight", 0.5)
                # Combined score: seed's score * weight + target's keyword score
                combined_score = (score * edge_weight) + t_score
                
                traversed_relpaths.add(target_relpath)
                traversed_nodes.append((combined_score, t_file, t_fm, t_body, f"edge ({etype} from {relpath})"))

    # 5. Pillar Auto-Injection
    # Check for any pillar nodes that match keywords or general topics
    for file_path, fm, body in nodes:
        if fm.get("node_type") == "pillar":
            nid = fm.get("id")
            relpath = f"pillar/{nid}"
            if relpath not in traversed_relpaths:
                p_score = score_node(fm, keywords)
                if p_score > 0.0 or any(kw in nid for kw in keywords):
                    traversed_relpaths.add(relpath)
                    traversed_nodes.append((p_score + 10.0, file_path, fm, body, "pillar_injection"))

    # Sort traversed context by score descending
    traversed_nodes.sort(key=lambda x: x[0], reverse=True)
    final_context_nodes = traversed_nodes[:limit]
    
    # 6. Output formatted context block
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
    print("Where source/citation-source is the parent source node in the derived_from chain.")
    
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
