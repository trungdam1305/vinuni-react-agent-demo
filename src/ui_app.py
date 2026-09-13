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
from app import run_react_agent, load_test_cases


st.set_page_config(
    page_title="ReAct Agent Demo - VinUni Academic Assistant",
    page_icon="🎓",
    layout="wide"
)

MODE_REACT = "react"
MODE_CHATBOT = "chatbot"

# Tên hiển thị thân thiện cho từng loại Test Case (thay vì hiện thẳng field "type" kỹ thuật)
TEST_CASE_LABELS = {
    "direct_query": ("💬 Câu hỏi chung", "Không cần gọi Tool — trả lời trực tiếp từ System Prompt"),
    "single_tool_query": ("🔍 Tra cứu học vụ", "Gọi 1 Tool: academic_query"),
    "appointment_booking": ("📅 Đặt lịch hẹn", "Gọi 1 Tool: schedule_appointment"),
    "multi_step_reasoning": ("🧩 Suy luận đa bước", "Tra cứu cố vấn → tự động đặt lịch (2 Tool nối tiếp)"),
    "edge_case_handling": ("⚠️ Trường hợp không tồn tại", "Kiểm tra Agent không bịa dữ liệu (NOT_FOUND)"),
}


@st.cache_resource
def get_agent_resources():
    provider = get_llm_provider()
    mcp_server = MCPAcademicServer()
    return provider, mcp_server


provider, mcp_server = get_agent_resources()

st.session_state.setdefault("messages", [])
st.session_state.setdefault("pending_query", None)
st.session_state.setdefault("run_mode", MODE_REACT)


def render_trace(trace_logs):
    """Vẽ chi tiết chuỗi Thought -> Action -> Observation -> Final Answer cho 1 phiên chạy."""
    for step in trace_logs:
        latency = step.get("latency_ms", 0)
        with st.container(border=True):
            if step.get("action_type") == "TOOL_EXECUTION":
                st.markdown(f"**Bước {step['step']} · 🛠️ Gọi Tool** &nbsp;·&nbsp; `{latency} ms`")
                st.caption(f"🧠 {step.get('thought', '')}")
                st.code(f"{step['tool_name']}({json.dumps(step['arguments'], ensure_ascii=False)})", language="python")
                st.markdown("👁️ **Observation**")
                st.json(step.get("observation", {}), expanded=False)
            else:
                st.markdown(f"**Bước {step['step']} · 🏁 Final Answer** &nbsp;·&nbsp; `{latency} ms`")
                st.caption(f"🧠 {step.get('thought', '')}")
                st.markdown(step.get("output", ""))


# ==============================================================================
# SIDEBAR — TRẠNG THÁI HỆ THỐNG, CHẾ ĐỘ CHẠY & CÂU HỎI MẪU
# ==============================================================================
with st.sidebar:
    st.subheader("⚙️ Trạng thái hệ thống")

    is_mock = isinstance(provider, MockOfflineProvider)
    model_name = getattr(provider, "model_name", "N/A")

    col1, col2 = st.columns(2)
    col1.metric("Provider", provider.__class__.__name__)
    col2.metric("Model", model_name if not is_mock else "Offline")

    if is_mock:
        st.warning("Chưa cấu hình API Key thật trong `.env` — đang chạy Offline Mock.", icon="⚠️")
    else:
        st.success("Đã kết nối LLM thật.", icon="✅")

    tools = mcp_server.list_tools()
    st.caption(f"🌐 MCP Server **{mcp_server.server_name}** · {len(tools)} Tools công bố")
    with st.expander("Xem Tool Schemas (JSON)"):
        st.json(tools)

    st.divider()

    st.subheader("🎛️ Chế độ chạy")
    st.radio(
        "Chọn chế độ:",
        [MODE_REACT, MODE_CHATBOT],
        format_func=lambda m: "🤖 ReAct Agent (có Tool qua MCP)" if m == MODE_REACT else "💬 Chatbot Baseline (không Tool)",
        key="run_mode",
        label_visibility="collapsed",
    )
    st.caption("Đổi bất cứ lúc nào — áp dụng ngay cho câu hỏi tiếp theo, không cần tải lại trang.")

    st.divider()

    st.subheader("🧪 Câu hỏi mẫu")
    try:
        test_cases = load_test_cases()
    except Exception:
        test_cases = []

    for tc in test_cases:
        question = tc.get("question", "")
        if question.strip().startswith("TODO"):
            continue
        title, desc = TEST_CASE_LABELS.get(tc["type"], (tc["type"], ""))
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(desc)
            if st.button("Dùng câu hỏi này →", key=f"tc_{tc['id']}", use_container_width=True):
                st.session_state.pending_query = question

    st.divider()
    if st.button("🗑️ Xóa lịch sử hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ==============================================================================
# MAIN — GIAO DIỆN CHAT SO SÁNH CHATBOT VS REACT AGENT
# ==============================================================================
st.title("🎓 Trợ lý Học vụ VinUni")
st.caption("ReAct Agent × MCP Server — Ngày 03 Lab: Chatbot vs ReAct Agent (MCP Enhanced)")

mode_label = "🤖 ReAct Agent" if st.session_state.run_mode == MODE_REACT else "💬 Chatbot Baseline"
st.caption(f"Đang chạy ở chế độ: **{mode_label}** — đổi ở sidebar bên trái.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("trace"):
            with st.expander("🔍 Xem chi tiết ReAct Trace"):
                render_trace(msg["trace"])

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
            if st.session_state.run_mode == MODE_REACT:
                trace_logs = run_react_agent(query, provider, mcp_server)
                final_entry = next((t for t in reversed(trace_logs) if t["action_type"] == "FINAL_ANSWER"), None)
                final_answer = final_entry["output"] if final_entry else "Không có câu trả lời."
                tool_calls = len([t for t in trace_logs if t["action_type"] == "TOOL_EXECUTION"])

                st.markdown(final_answer)
                st.caption(f"📊 {tool_calls} lượt gọi Tool · {len(trace_logs)} sự kiện trace")
                with st.expander("🔍 Xem chi tiết ReAct Trace", expanded=True):
                    render_trace(trace_logs)

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
