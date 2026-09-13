"""
🎨 STREAMLIT UI DEMO — REACT AGENT VS CHATBOT (DAY 03 LAB)
Giao diện web trực quan để chạy thử ReAct Agent kết nối MCP Server,
xem trực tiếp từng bước Thought -> Action -> Observation -> Final Answer.
"""

import os
import sys
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from mcp_server import MCPAcademicServer
from providers import get_llm_provider, MockOfflineProvider
from app import run_react_agent, run_baseline_chatbot, load_test_cases


st.set_page_config(
    page_title="ReAct Agent Demo - VinUni Academic Assistant",
    page_icon="🎓",
    layout="wide"
)


@st.cache_resource
def get_agent_resources():
    provider = get_llm_provider()
    mcp_server = MCPAcademicServer()
    return provider, mcp_server


provider, mcp_server = get_agent_resources()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = None


# ==============================================================================
# SIDEBAR — TRẠNG THÁI HỆ THỐNG & TEST CASES MẪU
# ==============================================================================
with st.sidebar:
    st.header("⚙️ Trạng thái hệ thống")

    is_mock = isinstance(provider, MockOfflineProvider)
    provider_label = provider.__class__.__name__
    model_name = getattr(provider, "model_name", "N/A")

    if is_mock:
        st.warning(f"🔌 Provider: **{provider_label}** (Offline Mock)\n\nChưa cấu hình API Key thật trong `.env`.")
    else:
        st.success(f"🔌 Provider: **{provider_label}**\n\n🧠 Model: `{model_name}`")

    tools = mcp_server.list_tools()
    st.info(f"🌐 MCP Server: **{mcp_server.server_name}**\n\n📦 Số Tools công bố: **{len(tools)}**")

    with st.expander("📋 Xem danh sách Tool Schemas"):
        st.json(tools)

    st.divider()
    st.header("🧪 Test Cases mẫu")
    try:
        test_cases = load_test_cases()
    except Exception:
        test_cases = []

    for tc in test_cases:
        question = tc.get("question", "")
        if question.strip().startswith("TODO"):
            continue
        label = f"[{tc['id']}] {tc['type']}"
        if st.button(label, key=f"tc_{tc['id']}", use_container_width=True):
            st.session_state.pending_query = question

    st.divider()
    if st.button("🗑️ Xóa lịch sử hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ==============================================================================
# MAIN — GIAO DIỆN CHAT SO SÁNH CHATBOT VS REACT AGENT
# ==============================================================================
st.title("🎓 ReAct Agent Demo — Trợ lý Học vụ VinUni")
st.caption("Ngày 03 Lab: Chatbot vs ReAct Agent (MCP Enhanced) — trực quan hóa vòng lặp Thought → Action → Observation")

mode = st.radio(
    "Chọn chế độ chạy:",
    ["🤖 ReAct Agent (Cấp 3 — có Tool qua MCP)", "💬 Chatbot Baseline (Cấp 2 — không Tool)"],
    horizontal=True
)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("trace"):
            with st.expander("🔍 Xem chi tiết ReAct Trace"):
                for step in msg["trace"]:
                    action_type = step.get("action_type")
                    latency = step.get("latency_ms", 0)
                    if action_type == "TOOL_EXECUTION":
                        st.markdown(f"**Step {step['step']} — 🛠️ TOOL_EXECUTION** `({latency} ms)`")
                        st.markdown(f"🧠 **Thought:** {step.get('thought', '')}")
                        st.code(f"{step['tool_name']}({json.dumps(step['arguments'], ensure_ascii=False)})", language="python")
                        st.markdown("👁️ **Observation:**")
                        st.json(step.get("observation", {}))
                    else:
                        st.markdown(f"**Step {step['step']} — 🏁 FINAL_ANSWER** `({latency} ms)`")
                        st.markdown(f"🧠 **Thought:** {step.get('thought', '')}")
                        st.markdown(f"**Output:** {step.get('output', '')}")
                    st.markdown("---")

query = st.chat_input("Nhập câu hỏi của sinh viên...")
if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Đang suy luận..."):
            if mode.startswith("🤖"):
                trace_logs = run_react_agent(query, provider, mcp_server)
                final_entry = next((t for t in reversed(trace_logs) if t["action_type"] == "FINAL_ANSWER"), None)
                final_answer = final_entry["output"] if final_entry else "Không có câu trả lời."
                tool_calls = len([t for t in trace_logs if t["action_type"] == "TOOL_EXECUTION"])

                st.markdown(final_answer)
                st.caption(f"📊 {tool_calls} lượt gọi Tool · {len(trace_logs)} sự kiện trace")
                with st.expander("🔍 Xem chi tiết ReAct Trace", expanded=True):
                    for step in trace_logs:
                        action_type = step.get("action_type")
                        latency = step.get("latency_ms", 0)
                        if action_type == "TOOL_EXECUTION":
                            st.markdown(f"**Step {step['step']} — 🛠️ TOOL_EXECUTION** `({latency} ms)`")
                            st.markdown(f"🧠 **Thought:** {step.get('thought', '')}")
                            st.code(f"{step['tool_name']}({json.dumps(step['arguments'], ensure_ascii=False)})", language="python")
                            st.markdown("👁️ **Observation:**")
                            st.json(step.get("observation", {}))
                        else:
                            st.markdown(f"**Step {step['step']} — 🏁 FINAL_ANSWER** `({latency} ms)`")
                            st.markdown(f"🧠 **Thought:** {step.get('thought', '')}")
                            st.markdown(f"**Output:** {step.get('output', '')}")
                        st.markdown("---")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": final_answer,
                    "trace": trace_logs
                })
            else:
                from prompts import CHATBOT_BASELINE_PROMPT
                response = provider.generate(query, system_prompt=CHATBOT_BASELINE_PROMPT)
                st.markdown(response)
                st.caption("💬 Chatbot Baseline — không có Tool, không truy cập dữ liệu thời gian thực")
                st.session_state.messages.append({"role": "assistant", "content": response, "trace": None})
