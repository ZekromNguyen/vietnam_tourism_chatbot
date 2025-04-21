import streamlit as st
import os
from dotenv import load_dotenv
from retriever import DocumentRetriever
from generator import ResponseGenerator

# Tải biến môi trường
load_dotenv()

# Kiểm tra khóa API GOOGLE
if not os.getenv("GOOGLE_API_KEY"):
    st.error("🔴 Vui lòng thiết lập GOOGLE_API_KEY trong tệp .env")
    st.info("Lấy khóa API Google tại: https://aistudio.google.com/app/apikey")
    st.stop()

# Khởi tạo các thành phần RAG với bộ nhớ đệm
@st.cache_resource
def initialize_rag():
    try:
        retriever = DocumentRetriever()
        if not retriever.vector_store:
            retriever.create_vector_store()
            if not retriever.vector_store:
                st.error("🚨 Không thể tạo kho vector. Vui lòng kiểm tra thư mục 'data'.")
                return None, None
        generator = ResponseGenerator(retriever)
        return retriever, generator
    except Exception as e:
        st.error(f"🔴 Lỗi khởi tạo: {e}")
        st.stop()

# Cấu hình trang
st.set_page_config(
    page_title="Khám Phá Việt Nam",
    page_icon="🇻🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh cho giao diện đẹp và thống nhất
st.markdown(
    """
    <style>
    /* Kiểu toàn cục */
    .stApp {
        background: linear-gradient(to bottom, rgba(10, 47, 66, 0.6), rgba(10, 47, 66, 0.6)), url("https://images.unsplash.com/photo-1509043759401-136742328bb3");
        background-size: cover;
        background-attachment: fixed;
        font-family: 'Source Sans Pro', sans-serif;
        color: #F5F6F5;
    }

    /* Kiểu chữ */
    h1, h2, h3, h4, p, div, span {
        color: #F5F6F5 !important;
    }

    /* Thanh bên */
    .css-1d391kg, .sidebar .sidebar-content {
        background: rgba(10, 47, 66, 0.85);
        padding: 15px;
        border-radius: 8px;
    }

    /* Khung trò chuyện */
    .stChatMessage {
        border-radius: 10px;
        padding: 10px 15px;
        margin: 8px 0;
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.2s ease;
    }

    .stChatMessage[data-testid="user"] {
        background: linear-gradient(145deg, rgba(69, 123, 157, 0.2), rgba(69, 123, 157, 0.1));
        border-left: 3px solid #457B9D;
    }

    .stChatMessage[data-testid="assistant"] {
        background: linear-gradient(145deg, rgba(244, 206, 141, 0.2), rgba(244, 206, 141, 0.1));
        border-left: 3px solid #D4A373;
    }

    /* Ô nhập liệu trò chuyện */
    .stChatInputContainer textarea {
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        background: rgba(255, 255, 255, 0.9) !important;
        color: #F5F6F5 !important;
        padding: 8px 12px !important;
        font-size: 14px !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
    }

    .stChatInputContainer textarea::placeholder {
        color: #A8B3C2 !important;
    }

    .stChatInputContainer textarea:focus {
        border-color: #D4A373 !important;
        box-shadow: 0 0 0 2px rgba(212, 163, 115, 0.2) !important;
    }

    /* Thẻ thông tin và điểm đến */
    .info-card, .destination-card {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 1px 6px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease;
    }

    .destination-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    /* Nút thu gọn trò chuyện */
    .chat-toggle-button {
        border-radius: 8px;
        background: #D4A373;
        color: #F5F6F5;
        font-weight: 500;
        padding: 8px 16px;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
        margin-bottom: 10px;
    }

    .chat-toggle-button:hover {
        background: #E8B923;
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    }

    /* Chân trang */
    .footer {
        text-align: center;
        padding: 12px;
        background: rgba(10, 47, 66, 0.8);
        border-radius: 8px;
        margin-top: 15px;
        font-size: 0.8em;
        position: relative;
    }

    .footer::before, .footer::after {
        content: '🌸';
        position: absolute;
        top: 12px;
        font-size: 1.2em;
    }

    .footer::before {
        left: 20px;
    }

    .footer::after {
        right: 20px;
    }

    /* Vòng xoay tải */
    .stSpinner > div {
        border-color: #D4A373 transparent transparent transparent !important;
    }

    /* Văn bản Markdown */
    .element-container div.stMarkdown, .element-container div.stMarkdown * {
        color: #F5F6F5 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Khởi tạo thành phần
retriever, generator = initialize_rag()
if not retriever or not generator:
    st.error("🚨 Ứng dụng không thể khởi tạo.")
    st.stop()

# Bố cục với cột
col1, col2 = st.columns([1, 2])

with col1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/2/21/Flag_of_Vietnam.svg", width=80)
    st.markdown("## 🇻🇳 Khám Phá Việt Nam")
    st.markdown(
        """
        <div class="info-card">
            <h4>🌏 Hướng Dẫn Du Lịch</h4>
            <p>Khám phá các danh lam, di tích văn hóa và những viên ngọc ẩn của các thành phố Việt Nam.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Điểm đến nổi bật
    st.markdown("### 📍 Điểm Đến Nổi Bật")
    destinations = {
        "Hà Nội": "Thủ đô lịch sử với văn hóa sôi động",
    "TP. Hồ Chí Minh": "Thành phố năng động với nét quyến rũ thuộc địa",
    "Vịnh Hạ Long": "Di sản UNESCO với làn nước ngọc lục bảo",
    "Hội An": "Phố cổ quyến rũ với đèn lồng rực rỡ",
    "Đà Nẵng": "Viên ngọc biển với bãi cát vàng",
    "Huế": "Thành phố cố đô với thành quách lịch sử",
    "Sa Pa": "Thị trấn núi với ruộng bậc thang tuyệt đẹp",
    "Nha Trang": "Thành phố biển sôi động",
    "Phú Quốc": "Thiên đường đảo nhiệt đới",
    "Đà Lạt": "Cao nguyên mát mẻ với vẻ đẹp hoa",
    "Đồng Bằng Sông Cửu Long": "Vùng sông nước với chợ nổi độc đáo",
    "Côn Đảo": "Quần đảo hoang sơ với lịch sử và biển xanh",
    "Phong Nha - Kẻ Bàng": "Vườn quốc giBàngi hang động lớn nhất thế giới"
    }
    for dest, desc in destinations.items():
        st.markdown(
            f"""
            <div class="destination-card">
                <b>{dest}</b>
                <p style="font-size: 0.8em; margin: 4px 0 0 0;">{desc}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col2:
    st.markdown("### Khám Phá Các Điểm Tham Quan Nổi Tiếng")
    st.markdown("*Hỏi về các danh thắng, di tích hoặc địa điểm văn hóa tại các thành phố Việt Nam.*")

    # Trạng thái thu gọn trò chuyện
    if "chat_minimized" not in st.session_state:
        st.session_state.chat_minimized = False

    # Nút thu gọn/mở rộng trò chuyện
    if st.session_state.chat_minimized:
        if st.button("💬 Mở Trò Chuyện", key="expand_chat", help="Mở khung trò chuyện"):
            st.session_state.chat_minimized = False
    else:
        st.markdown(
            '<button class="chat-toggle-button">Thu Gọn Trò Chuyện</button>',
            unsafe_allow_html=True,
        )
        if st.button("", key="minimize_chat", help="Thu gọn khung trò chuyện", type="primary"):
            st.session_state.chat_minimized = True

        # Khởi tạo lịch sử trò chuyện
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": """Xin chào! 👋 Chào mừng đến với Khám Phá Việt Nam!

Tôi là hướng dẫn viên ảo của bạn, chuyên về các điểm tham quan nổi tiếng tại Việt Nam. Hỏi tôi về danh lam, di tích lịch sử hoặc các địa điểm văn hóa ở Hà Nội, Hội An, Huế và hơn thế nữa.

**Gợi ý câu hỏi:**
- Những điểm phải đến ở TP. Hồ Chí Minh?
- Lịch sử của Phố cổ Hội An?
- Chùa nổi tiếng nhất ở Hà Nội?
- Điều gì làm Vịnh Hạ Long đặc biệt?
                    """
                }
            ]

        # Hiển thị lịch sử trò chuyện
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Xử lý đầu vào người dùng
        if prompt := st.chat_input("Hỏi về một điểm tham quan ở Việt Nam..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("Đang tìm kiếm thông tin..."):
                    response = generator.generate_response(prompt)
                    st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Chân trang
st.markdown(
    """
    <div class="footer">
        <p>© 2025 Khám Phá Việt Nam | Được hỗ trợ bởi AI | Khám phá vẻ đẹp Việt Nam</p>
    </div>
    """,
    unsafe_allow_html=True,
)