import streamlit as st
from handlers.monitor import fetch_all_monitoring_data
from utils.components import page_header, page_footer, get_base64_image

st.set_page_config(
    page_title="Admin Dashboard | Cost & Traces",
    page_icon="🛡️",
    layout="wide"
)

logo_base64 = get_base64_image("kayfa logo.svg")
page_header(logo_base64, "Admin Dashboard")

st.title("🛡️ Admin Dashboard")
st.markdown("Monitor user conversations, tool traces, and API costs.")

# ─── Auth Check ───────────────────────────────────────────────────────────────
if not st.session_state.get("logged_in") or st.session_state.get("user_role") != "admin":
    st.error("Access Denied. You must be an administrator to view this page.")
    st.stop()

db_client = st.session_state.resources["db"]

# ─── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def get_dashboard_data():
    return fetch_all_monitoring_data(db_client)

data = get_dashboard_data()

if not data:
    st.info("No chat data available.")
    st.stop()

# ─── Global Stats ─────────────────────────────────────────────────────────────
total_cost = sum([d["total_cost"] for d in data])
total_in_tokens = sum([d["total_input_tokens"] for d in data])
total_out_tokens = sum([d["total_output_tokens"] for d in data])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total API Cost", f"${total_cost:.4f}")
col2.metric("Total Input Tokens", f"{total_in_tokens:,}")
col3.metric("Total Output Tokens", f"{total_out_tokens:,}")
col4.metric("Total Conversations", len(data))

st.divider()

# ─── User Selection ───────────────────────────────────────────────────────────
user_options = list(set([(d["user_id"], d["user_name"]) for d in data]))
user_options.sort(key=lambda x: x[1])

st.subheader("User Analysis")
selected_user_tuple = st.selectbox(
    "Select a User to monitor:", 
    user_options, 
    format_func=lambda x: f"{x[1]} ({x[0][:8]}...)"
)

if not selected_user_tuple:
    st.stop()

selected_user_id = selected_user_tuple[0]
user_chats = [d for d in data if d["user_id"] == selected_user_id]

# User stats
user_cost = sum([c["total_cost"] for c in user_chats])
st.markdown(f"**{selected_user_tuple[1]}'s Total Cost:** `${user_cost:.4f}` across {len(user_chats)} conversations.")

# ─── Chat Selection ───────────────────────────────────────────────────────────
st.subheader("Conversations")
selected_chat_id = st.selectbox(
    "Select a Conversation:", 
    [c["chat_id"] for c in user_chats],
    format_func=lambda x: next(c["chat_title"] for c in user_chats if c["chat_id"] == x)
)

selected_chat = next(c for c in user_chats if c["chat_id"] == selected_chat_id)

st.markdown(f"**Chat Cost:** `${selected_chat['total_cost']:.4f}` | **Tokens:** {selected_chat['total_input_tokens']} In, {selected_chat['total_output_tokens']} Out")

st.divider()

# ─── Trace Visualizer ─────────────────────────────────────────────────────────
st.subheader("Execution Trace")

# CSS for Timeline
st.markdown("""
<style>
.trace-timeline {
    border-left: 2px solid #e2e8f0;
    margin-left: 10px;
    padding-left: 20px;
    position: relative;
    font-family: 'Inter', Tajawal, sans-serif;
    direction: ltr;
}
.trace-item {
    position: relative;
    margin-bottom: 25px;
}
.trace-dot {
    position: absolute;
    left: -27px;
    top: 5px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
}
.dot-user { background-color: #6366f1; }
.dot-think { background-color: #eab308; }
.dot-tool { background-color: #3b82f6; }
.dot-result { background-color: #10b981; }
.dot-final { background-color: #ef4444; }

.trace-label {
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 5px;
    letter-spacing: 0.05em;
}
.trace-content {
    font-size: 14px;
    color: #334155;
    background: white;
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #f1f5f9;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.trace-code {
    background: #f8fafc;
    padding: 10px;
    border-radius: 6px;
    font-family: monospace;
    font-size: 13px;
    color: #475569;
    white-space: pre-wrap;
    border: 1px solid #e2e8f0;
    margin-bottom: 5px;
}
.trace-footer {
    font-size: 12px;
    color: #64748b;
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px dashed #cbd5e1;
    display: flex;
    gap: 15px;
}
</style>
""", unsafe_allow_html=True)

if not selected_chat["traces"]:
    st.info("No traces found for this conversation.")

for idx, trace in enumerate(selected_chat["traces"]):
    with st.expander(f"Prompt {idx+1}: {trace['user_prompt'][:50]}...", expanded=True):
        html = '<div class="trace-timeline">'
        
        # User Prompt
        html += f"""<div class="trace-item">
<div class="trace-dot dot-user"></div>
<div class="trace-label">USER PROMPT</div>
<div class="trace-content" dir="auto">

{trace['user_prompt']}

</div>
</div>"""
        
        # Thinking
        if trace.get('think'):
            html += f"""<div class="trace-item">
<div class="trace-dot dot-think"></div>
<div class="trace-label">REASONING (THINKING)</div>
<div class="trace-content" dir="auto" style="background:#fefce8; border-color:#fef08a;">

{trace['think']}

</div>
</div>"""
        
        # Tool Calls
        for tcall in trace['tool_calls']:
            html += f"""<div class="trace-item">
<div class="trace-dot dot-tool"></div>
<div class="trace-label">TOOL CALL</div>
<div class="trace-code">{tcall['name']}({tcall['args']})</div>
</div>"""
            
        # Tool Results
        for tresult in trace['tool_results']:
            html += f"""<div class="trace-item">
<div class="trace-dot dot-result"></div>
<div class="trace-label">TOOL RESULT ({tresult['name']})</div>
<div class="trace-code">{tresult['content']}</div>
</div>"""
            
        # Final Response
        html += f"""<div class="trace-item">
<div class="trace-dot dot-final"></div>
<div class="trace-label">FINAL RESPONSE TO USER</div>
<div class="trace-content" dir="auto">

{trace['final_response']}

</div>
</div>"""
        
        # Footer stats
        html += f"""<div class="trace-footer">
<span>Tokens: {trace['input_tokens']} in, {trace['output_tokens']} out</span>
<span>Cost: ${trace['cost']:.4f}</span>
<span>Tool Calls: {len(trace['tool_calls'])}</span>
<span>Latency: {trace.get('latency', 0.0):.2f}s</span>
</div>"""
        
        html += '</div>'
        
        st.markdown(html, unsafe_allow_html=True)

page_footer(logo_base64)
