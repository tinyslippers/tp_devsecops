import json, re, sys

def p95(values):
    values = sorted(v for v in values if isinstance(v, int))
    if not values:
        return 0
    idx = int(0.95 * (len(values) - 1))
    return values[idx]

def main(path_in, path_out):
    logs = []
    with open(path_in, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # On ignore les lignes qui ne sont pas du JSON
            if "{" not in line:
                continue
            try:
                # On extrait la partie JSON après le prefix 'catalog | '
                json_part = line.split("|")[-1].strip()
                logs.append(json.loads(json_part))
            except Exception:
                pass

    status = [x.get("status") for x in logs if isinstance(x, dict)]
    lat = [x.get("latency_ms") for x in logs if isinstance(x, dict)]
    queries = [x.get("query", "") for x in logs if isinstance(x, dict)]

    count_5xx = sum(1 for s in status if isinstance(s, int) and s >= 500)
    p95_lat = p95([v for v in lat if isinstance(v, int)])
    
    # Détection de patterns suspects
    traversal_hits = sum(1 for q in queries if re.search(r"\.\./", q or ""))
    cmd_hits = sum(1 for q in queries if "cmd=" in (q or ""))

    report = {
        "n_logs": len(logs),
        "count_5xx": count_5xx,
        "p95_latency_ms": p95_lat,
        "patterns": {
            "path_traversal_hits": traversal_hits,
            "cmd_param_hits": cmd_hits
        }
    }

    with open(path_out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python monitoring/log_metrics.py <in.jsonl> <out.json>")
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
