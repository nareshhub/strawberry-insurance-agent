import sqlite3
import json

def main():
    conn = sqlite3.connect("strawberry_agent/.adk/session.db")
    cursor = conn.cursor()
    
    # Get the latest session_id
    cursor.execute("SELECT id, user_id, update_time FROM sessions ORDER BY update_time DESC LIMIT 1")
    latest_sess = cursor.fetchone()
    if not latest_sess:
        print("No sessions found.")
        conn.close()
        return
        
    sess_id, user_id, ut = latest_sess
    print(f"Latest Session: {sess_id} | User: {user_id} | Updated: {ut}\n")
    
    # Get all events for this session ordered by timestamp
    cursor.execute(
        "SELECT id, timestamp, event_data FROM events WHERE session_id = ? ORDER BY timestamp ASC",
        (sess_id,)
    )
    events = cursor.fetchall()
    
    for ev_id, ts, data_json in events:
        data = json.loads(data_json)
        author = data.get("author", "unknown")
        node_path = data.get("node_info", {}).get("path", "")
        print(f"\n[{author}] @ node: {node_path}")
        
        content = data.get("content")
        if content and "parts" in content:
            for part in content["parts"]:
                if "text" in part:
                    print(f"  Text: {part['text']}")
                if "function_call" in part:
                    fc = part["function_call"]
                    print(f"  Tool Call: {fc.get('name')}({fc.get('args')})")
                if "function_response" in part:
                    fr = part["function_response"]
                    print(f"  Tool Response: {fr.get('name')} -> {fr.get('response')}")
                    
        output = data.get("output")
        if output:
            print(f"  Output: {output}")
            
    conn.close()

if __name__ == "__main__":
    main()
