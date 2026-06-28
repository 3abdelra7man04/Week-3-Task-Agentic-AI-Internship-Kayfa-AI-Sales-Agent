from models.UserModel import UserModel
from models.ChatModel import ChatModel
from datetime import datetime

def parse_iso(ts_str):
    if not ts_str:
        return None
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return None

def fetch_all_monitoring_data(db_client):
    user_model = UserModel.create_instance(db_client)
    chat_model = ChatModel.create_instance(db_client)
    
    users = user_model.get_all_users()
    chats = chat_model.get_all_chats()
    
    # Map user id to name
    user_map = {str(u.id): u.user_name for u in users}
    
    dashboard_data = []
    
    for chat in chats:
        c_id = str(chat.get("_id", ""))
        c_user_id = str(chat.get("chat_user_id", ""))
        c_user_name = user_map.get(c_user_id, "Unknown User")
        c_title = chat.get("chat_title") or "Untitled Chat"
        
        history = chat.get("chat_history", [])
            
        traces = []
        chat_input_tokens = 0
        chat_output_tokens = 0
        chat_cost = 0.0
        
        current_trace = None
        
        for raw_msg in history:
            kind = raw_msg.get("kind")
            parts = raw_msg.get("parts", [])
            msg_ts_str = raw_msg.get("timestamp")
            msg_time = parse_iso(msg_ts_str)
            
            i_tok = 0
            o_tok = 0
            cost = 0.0
            
            if kind == "response":
                usage = raw_msg.get("usage", {})
                i_tok = usage.get("request_tokens", usage.get("input_tokens", 0))
                o_tok = usage.get("response_tokens", usage.get("output_tokens", 0))
                cost = raw_msg.get("provider_details", {}).get("cost", 0.0)
            
            if kind == "request":
                for part in parts:
                    if part.get("part_kind") == "user-prompt":
                        if current_trace:
                            if current_trace.get("start_time") and current_trace.get("end_time"):
                                current_trace["latency"] = (current_trace["end_time"] - current_trace["start_time"]).total_seconds()
                            traces.append(current_trace)
                        current_trace = {
                            "user_prompt": part.get("content", ""),
                            "tool_calls": [],
                            "tool_results": [],
                            "think": "",
                            "final_response": "",
                            "input_tokens": 0,
                            "output_tokens": 0,
                            "cost": 0.0,
                            "latency": 0.0,
                            "start_time": msg_time,
                            "end_time": msg_time
                        }
                    elif part.get("part_kind") == "tool-return":
                        if current_trace:
                            current_trace["tool_results"].append({
                                "name": part.get("tool_name", ""),
                                "content": str(part.get("content", ""))
                            })
                            if msg_time:
                                current_trace["end_time"] = msg_time
                            
            elif kind == "response":
                if current_trace and msg_time:
                    current_trace["end_time"] = msg_time
                    
                for part in parts:
                    if part.get("part_kind") == "text":
                        if current_trace:
                            current_trace["final_response"] += str(part.get("content", ""))
                    elif part.get("part_kind") == "tool-call":
                        if current_trace:
                            current_trace["tool_calls"].append({
                                "name": part.get("tool_name", ""),
                                "args": str(part.get("args", {}))
                            })
                    elif part.get("part_kind") == "thinking":
                        if current_trace:
                            current_trace["think"] += str(part.get("content", ""))
            
            if current_trace:
                current_trace["input_tokens"] += i_tok
                current_trace["output_tokens"] += o_tok
                current_trace["cost"] += float(cost) if cost else 0.0
                
            chat_input_tokens += i_tok
            chat_output_tokens += o_tok
            chat_cost += float(cost) if cost else 0.0

        if current_trace:
            if current_trace.get("start_time") and current_trace.get("end_time"):
                current_trace["latency"] = (current_trace["end_time"] - current_trace["start_time"]).total_seconds()
            traces.append(current_trace)
            
        dashboard_data.append({
            "chat_id": c_id,
            "user_id": c_user_id,
            "user_name": c_user_name,
            "chat_title": c_title,
            "total_input_tokens": chat_input_tokens,
            "total_output_tokens": chat_output_tokens,
            "total_cost": chat_cost,
            "traces": traces,
            "raw_history": history
        })
        
    return dashboard_data
