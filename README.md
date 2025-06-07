# Vietnam Tourism Chatbot 🇻🇳

Chatbot hướng dẫn du lịch Việt Nam với khả năng trả lời câu hỏi về các điểm tham quan, gợi ý tour du lịch và hỗ trợ nhập liệu bằng giọng nói.

## Tính năng

1. **Thông tin du lịch**: Cung cấp thông tin chi tiết về các địa điểm du lịch, di tích lịch sử, văn hóa và ẩm thực của Việt Nam.

2. **Gợi ý tour du lịch**: Tìm kiếm và gợi ý các tour du lịch phù hợp dựa trên yêu cầu của người dùng như:
   - Điểm đến mong muốn
   - Số lượng khách
   - Ngân sách
   - Thời gian

3. **Voice-to-text**: Cho phép người dùng đặt câu hỏi bằng giọng nói thay vì gõ, hỗ trợ tiếng Việt.

## Tính năng mới

### Cải thiện nhận dạng giọng nói
Chức năng nhận dạng giọng nói đã được cập nhật với các cải tiến:
- Tăng thời gian lắng nghe và điều chỉnh nhiễu nền để nhận dạng chính xác hơn
- Hậu xử lý kết quả nhận dạng để sửa các lỗi phổ biến
- Thử nghiệm với nhiều tùy chọn ngôn ngữ khác nhau (vi-VN, vi)
- Tự động chuẩn hóa các tên địa điểm thường bị nhận dạng sai

### Dữ liệu mới
Bổ sung thêm dữ liệu về các điểm du lịch:
- Vũng Tàu: thông tin chi tiết về bãi biển, ẩm thực, địa điểm tham quan
- Đà Nẵng: thông tin về điểm đến nổi bật, lễ hội, thời điểm du lịch

## Cài đặt

1. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```

2. Để sử dụng tính năng voice-to-text, cần cài đặt thêm:
   - Ubuntu/Debian: `apt install portaudio19-dev python3-pyaudio`
   - MacOS: `brew install portaudio && pip install pyaudio`
   - Windows: `pip install pipwin && pipwin install pyaudio`

3. Tạo file `.env` với khóa API Google:
   ```
   GOOGLE_API_KEY=your_google_api_key
   ```

4. Khởi chạy ứng dụng:
   ```
   streamlit run vietnam_tourism_app.py
   ```

## Cách sử dụng

Người dùng có thể:
- Hỏi về các điểm tham quan nổi tiếng tại Việt Nam
- Yêu cầu gợi ý tour du lịch, ví dụ:
  - "Gợi ý tour du lịch Đà Nẵng cho 4 người"
  - "Có tour nào đến Phú Quốc với giá dưới 2 triệu không?"
  - "Tôi muốn tìm tour đi Hạ Long"
- Sử dụng nút 🎙️ để nói câu hỏi thay vì gõ

## Kiến trúc

Chatbot sử dụng kiến trúc RAG (Retrieval-Augmented Generation) kết hợp với API tour du lịch:
- **Retriever**: Tìm kiếm thông tin từ cơ sở dữ liệu vector về du lịch Việt Nam
- **Generator**: Tạo câu trả lời sử dụng Google Gemini
- **Tour API**: Kết nối với API bên ngoài để lấy thông tin về các tour du lịch hiện có
- **Voice Recognition**: Sử dụng Google Speech Recognition API để chuyển đổi giọng nói thành văn bản

## Tác giả

Phát triển bởi Nguyễn Đức Tuyên cho dự án EXE201. 