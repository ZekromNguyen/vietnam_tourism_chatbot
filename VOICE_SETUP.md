# Hướng dẫn cài đặt tính năng Voice-to-Text

Tính năng nhận dạng giọng nói cho phép bạn nói chuyện với chatbot thay vì gõ. Tính năng này yêu cầu cài đặt thêm các thư viện phụ thuộc.

## Các thư viện cần thiết

1. **SpeechRecognition**: Thư viện Python để nhận dạng giọng nói
2. **PyAudio**: Thư viện để ghi âm và phát âm thanh 

## Hướng dẫn cài đặt theo hệ điều hành

### Windows

1. Cài đặt pipwin (công cụ hỗ trợ cài đặt PyAudio):
   ```
   pip install pipwin
   ```

2. Cài đặt PyAudio thông qua pipwin:
   ```
   pipwin install pyaudio
   ```

3. Cài đặt SpeechRecognition:
   ```
   pip install SpeechRecognition
   ```

### macOS

1. Cài đặt portaudio thông qua Homebrew:
   ```
   brew install portaudio
   ```

2. Cài đặt PyAudio và SpeechRecognition:
   ```
   pip install pyaudio SpeechRecognition
   ```

### Linux (Ubuntu/Debian)

1. Cài đặt các thư viện phụ thuộc:
   ```
   sudo apt-get install python3-pyaudio portaudio19-dev
   ```

2. Cài đặt SpeechRecognition:
   ```
   pip install SpeechRecognition
   ```

## Kiểm tra cài đặt

Sau khi cài đặt, bạn có thể kiểm tra với đoạn code Python sau:

```python
import speech_recognition as sr

# Tạo một đối tượng recognizer
r = sr.Recognizer()

# Kiểm tra nếu có thể truy cập microphone
try:
    with sr.Microphone() as source:
        print("Kiểm tra microphone thành công!")
        print("Nói một câu...")
        audio = r.listen(source)
        print("Đã ghi âm, đang nhận dạng...")
        
        # Nhận dạng bằng Google Speech Recognition
        text = r.recognize_google(audio, language="vi-VN")
        print(f"Nhận dạng: {text}")
except Exception as e:
    print(f"Lỗi: {e}")
```

## Xử lý sự cố

### Không tìm thấy microphone

- Kiểm tra xem microphone đã được kết nối đúng cách chưa
- Kiểm tra quyền truy cập microphone của ứng dụng
- Đảm bảo không có ứng dụng khác đang sử dụng microphone

### Lỗi khi cài đặt PyAudio

- Windows: Nếu gặp lỗi khi cài đặt trực tiếp, hãy thử sử dụng pipwin
- macOS: Đảm bảo portaudio đã được cài đặt trước khi cài PyAudio
- Linux: Cần cài đặt các gói phát triển trước khi cài đặt PyAudio

### Lỗi nhận dạng giọng nói

- Đảm bảo bạn có kết nối internet ổn định (Google Speech API yêu cầu internet)
- Nói rõ ràng và không quá nhanh
- Điều chỉnh mức âm lượng microphone 