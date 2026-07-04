import sqlite3
import json

def main():
    conn = sqlite3.connect("strawberry_agent/.adk/session.db")
    cursor = conn.cursor()
    
    # Query all events in the database
    cursor.execute("SELECT session_id, timestamp, event_data FROM events ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    
    print(f"Total events in database: {len(rows)}\n")
    
    # Group events by session_id
    sessions = {}
    for sess_id, ts, data_json in rows:
        if sess_id not in sessions:
            sessions[sess_id] = []
        sessions[sess_id].append(json.loads(data_json))
        
    for sess_id, events in sessions.items():
        # Check if this session contains the prompt injection query
        has_injection_query = False
        has_approved_response = False
        
        for event in events:
            content = event.get("content")
            if content and "parts" in content:
                for part in content["parts"]:
                    text = part.get("text", "")
                    if "Ignore instructions" in text:
                        has_injection_query = True
            
            output = event.get("output")
            if output:
                output_str = str(output)
                if "Claim Approved: We have approved your claim for $200.0" in output_str:
                    has_approved_response = True
                    
        if has_injection_query:
            print("=" * 80)
            print(f"SESSION WITH INJECTION QUERY: {sess_id}")
            print("=" * 80)
            for event in events:
                author = event.get("author", "unknown")
                node_path = event.get("node_info", {}).get("path", "")
                print(f"[{author}] @ {node_path}")
                content = event.get("content")
                if content and "parts" in content:
                    for part in content["parts"]:
                        if "text" in part:
                            print(f"  Text: {part['text']}")
                        if "function_call" in part:
                            print(f"  Tool Call: {part['function_call'].get('name')}({part['function_call'].get('args')})")
                        if "function_response" in part:
                            print(f"  Tool Response: {part['function_response'].get('name')} -> {part['function_response'].get('response')}")
                output = event.get("output")
                if output:
                    print(f"  Output: {output}")
            print("-" * 80)
            
    conn.close()

if __name__ == "__main__":
    main()
