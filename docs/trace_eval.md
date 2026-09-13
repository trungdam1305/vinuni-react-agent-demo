# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Đàm Quang Trung  
> **Mã Sinh Viên / Mã Học viên:** 2A202602525  
> **Chủ đề Lựa chọn:** Gợi ý 1.1 — Trợ lý Học vụ & Tra cứu Lịch thi VinUni (Tra cứu GPA/hồ sơ sinh viên và đặt lịch tư vấn học vụ với Cố vấn)  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | Kịch bản đặt lịch tư vấn (TC04) đòi hỏi 2 bước suy luận nối tiếp: (1) tra cứu hồ sơ sinh viên để xác định cố vấn học tập phụ trách, (2) dùng đúng tên cố vấn đó để đặt lịch hẹn. Không đạt mức 5/5 vì chuỗi suy luận còn ngắn (2 bước), chưa có lập kế hoạch (planning) phức tạp nhiều nhánh. |
| **2. Tool Interaction** | 5 / 5 | Hệ thống bắt buộc phải gọi 2 Tool riêng biệt qua MCP Server: `academic_query` (đọc dữ liệu học vụ) và `schedule_appointment` (ghi/hành động đặt lịch). Dữ liệu sinh viên (GPA, cố vấn...) không nằm sẵn trong System Prompt nên Agent luôn phải truy vấn nguồn ngoài để trả lời chính xác. |
| **3. Dynamic Decision** | 4 / 5 | Tham số `advisor_name` dùng ở bước đặt lịch (TC04) phụ thuộc vào Observation trả về từ bước tra cứu trước đó — Agent phải đọc kết quả Tool rồi mới quyết định được tham số cho hành động kế tiếp, thay vì dùng giá trị cố định. Không đạt 5/5 vì số nhánh quyết định trong bài toán còn giới hạn (chủ yếu SUCCESS/NOT_FOUND). |
| **4. Long Horizon Goal** | 2 / 5 | Mỗi phiên chỉ giải quyết một yêu cầu ngắn hạn (tra cứu và/hoặc đặt lịch trong cùng lượt hội thoại), không cần duy trì bộ nhớ hay mục tiêu xuyên suốt nhiều phiên/nhiều ngày như một Autonomous Agent (Cấp 4). |
| **TỔNG ĐIỂM AGENTIC FIT** | **15 / 20** | Tổng điểm 15/20 > 12/20 → Bài toán **phù hợp triển khai Agentic System (ReAct Agent)** thay vì chỉ dùng Chatbot Baseline, do có nhu cầu Tool Interaction cao và quyết định phụ thuộc dữ liệu động ở bước sau. |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật (OpenAI `gpt-4o-mini`, Test Case **TC04 — suy luận ReAct đa bước**, thể hiện đầy đủ chuỗi `Thought → Action → Observation` lặp 2 vòng rồi kết thúc bằng `Final Answer`):

> 🔍 **Điểm cần chú ý:** Tham số `advisor_name: "TS. Lê Thị B"` ở Step 2 **không có trong câu hỏi gốc** của sinh viên — Agent phải đọc được giá trị này từ `observation` của Step 1 rồi mới quyết định được tham số cho hành động kế tiếp. Đây chính là bằng chứng của tiêu chí *Dynamic Decision* và *Multi-step Reasoning*.

```json
[
  {
    "step": 1,
    "query": "Hãy tra cứu cố vấn học tập của sinh viên SV2026002 rồi giúp tôi đặt lịch hẹn tư vấn học vụ với cố vấn đó vào lúc 09:00 ngày 20/09/2026.",
    "action_type": "TOOL_EXECUTION",
    "thought": "OpenAI quyết định gọi công cụ 'academic_query' với tham số: {\"student_id\": \"SV2026002\"}",
    "tool_name": "academic_query",
    "arguments": {
      "student_id": "SV2026002"
    },
    "observation": {
      "status": "SUCCESS",
      "student_id": "SV2026002",
      "data": {
        "full_name": "Trần Thị Bình",
        "class": "AI-K4",
        "gpa": 3.6,
        "email": "binh.tt@vinuni.edu.vn",
        "status": "Đang học",
        "advisor": "TS. Lê Thị B"
      }
    },
    "latency_ms": 2367.6
  },
  {
    "step": 2,
    "query": "Hãy tra cứu cố vấn học tập của sinh viên SV2026002 rồi giúp tôi đặt lịch hẹn tư vấn học vụ với cố vấn đó vào lúc 09:00 ngày 20/09/2026.",
    "action_type": "TOOL_EXECUTION",
    "thought": "OpenAI quyết định gọi công cụ 'schedule_appointment' với tham số: {\"student_id\": \"SV2026002\", \"datetime_str\": \"09:00 20/09/2026\", \"advisor_name\": \"TS. Lê Thị B\"}",
    "tool_name": "schedule_appointment",
    "arguments": {
      "student_id": "SV2026002",
      "datetime_str": "09:00 20/09/2026",
      "advisor_name": "TS. Lê Thị B"
    },
    "observation": {
      "status": "SUCCESS",
      "booking_id": "BK-SV2026002-99",
      "student_id": "SV2026002",
      "datetime": "09:00 20/09/2026",
      "advisor": "TS. Lê Thị B",
      "message": "Đặt lịch thành công cho sinh viên SV2026002 với TS. Lê Thị B vào lúc 09:00 20/09/2026."
    },
    "latency_ms": 1348.76
  },
  {
    "step": 4,
    "query": "Hãy tra cứu cố vấn học tập của sinh viên SV2026002 rồi giúp tôi đặt lịch hẹn tư vấn học vụ với cố vấn đó vào lúc 09:00 ngày 20/09/2026.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "Đặt lịch thành công cho sinh viên SV2026002 với TS. Lê Thị B vào lúc 09:00 20/09/2026.",
    "latency_ms": 10.0
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (OpenAI `gpt-4o-mini`).
- **Tổng số Test Cases đã chạy thành công:** 5 / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** 5 lượt (TC02: `academic_query`; TC03: `schedule_appointment`; TC04: `academic_query` → `schedule_appointment` (2 lượt, suy luận đa bước); TC05: `academic_query`. TC01 không gọi Tool vì là câu hỏi chung — Agent tự nhận biết trả lời trực tiếp).
- **Tổng số sự kiện ghi trong `docs/trace_waterfall.json`:** 10 sự kiện (5 `TOOL_EXECUTION` + 5 `FINAL_ANSWER`), mọi sự kiện đều có trường `thought` ghi lại bước suy luận.
- **Kết quả đẩy Repo nộp bài:** [x] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân: https://github.com/trungdam1305/K4A-Day03-DamQuangTrung-2A202602525

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
