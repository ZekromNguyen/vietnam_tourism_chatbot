import speech_recognition as sr
import os
import tempfile
import time
import re

class VoiceRecognition:
    def __init__(self, language="vi-VN"):
        """
        Khởi tạo nhận dạng giọng nói
        
        Args:
            language: Ngôn ngữ nhận dạng (mặc định: Tiếng Việt)
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        
        # Tinh chỉnh các thông số cho nhận dạng tốt hơn
        self.recognizer.pause_threshold = 0.8  # Cho phép tạm dừng lâu hơn giữa các từ
        self.recognizer.energy_threshold = 300  # Mức năng lượng phát hiện giọng nói (mặc định là 300)
        # Điều chỉnh để nhận biết rõ ràng hơn các âm thanh mềm
        self.recognizer.dynamic_energy_threshold = True
        
        # Từ điển sửa lỗi phổ biến
        self.corrections = {
            "sai gòn": "Sài Gòn",
            "hồ chí min": "Hồ Chí Minh",
            "ha noi": "Hà Nội",
            "vung tau": "Vũng Tàu",
            "da nang": "Đà Nẵng",
            "nha trang": "Nha Trang",
            "huế": "Huế",
            "hoi an": "Hội An",
            "đà lạt": "Đà Lạt",
            "phú quốc": "Phú Quốc",
            "cần thơ": "Cần Thơ"
        }
    
    def post_process_text(self, text):
        """
        Hậu xử lý văn bản để cải thiện chất lượng nhận dạng
        
        Args:
            text: Văn bản cần xử lý
            
        Returns:
            Văn bản đã được xử lý
        """
        if not text:
            return text
        
        # Sửa lỗi dấu câu thiếu
        processed_text = text
        
        # Đảm bảo chữ cái đầu tiên là viết hoa
        if len(processed_text) > 0:
            processed_text = processed_text[0].upper() + processed_text[1:]
        
        # Thêm dấu chấm cuối câu nếu cần
        if not processed_text.endswith(('.', '?', '!')):
            processed_text += '.'
            
        # Sửa các từ thường bị nhận dạng sai
        for incorrect, correct in self.corrections.items():
            # Sử dụng regex để tìm kiếm không phân biệt hoa thường
            pattern = re.compile(re.escape(incorrect), re.IGNORECASE)
            processed_text = pattern.sub(correct, processed_text)
            
        # Sửa khoảng trắng thừa
        processed_text = re.sub(r'\s+', ' ', processed_text).strip()
        
        return processed_text
    
    def recognize_from_microphone(self, timeout=7, adjust_duration=1.0):
        """
        Nhận dạng giọng nói từ microphone
        
        Args:
            timeout: Thời gian ghi âm tối đa (giây)
            adjust_duration: Thời gian điều chỉnh nhiễu nền (giây)
        
        Returns:
            Văn bản nhận dạng từ giọng nói hoặc None nếu thất bại
        """
        try:
            with sr.Microphone() as source:
                print("Đang lắng nghe...")
                # Điều chỉnh ngưỡng năng lượng âm thanh - tăng thời gian để điều chỉnh tốt hơn
                self.recognizer.adjust_for_ambient_noise(source, duration=adjust_duration)
                print("Đã điều chỉnh nhiễu nền, sẵn sàng ghi âm...")
                # Lắng nghe audio với thời gian chờ lâu hơn
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                print("Đã ghi âm, đang xử lý...")
                
            # Thử nhận dạng với các tùy chọn ngôn ngữ khác nhau nếu cần
            text = None
            try:
                # Nhận dạng bằng Google Speech Recognition
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"Nhận dạng ban đầu: {text}")
            except sr.UnknownValueError:
                # Nếu thất bại với tiếng Việt, thử với tiếng Việt khác phương ngữ
                try:
                    alt_language = "vi" if self.language == "vi-VN" else "vi-VN"
                    print(f"Thử lại với ngôn ngữ: {alt_language}")
                    text = self.recognizer.recognize_google(audio, language=alt_language)
                    print(f"Nhận dạng với {alt_language}: {text}")
                except:
                    pass
            
            # Áp dụng hậu xử lý
            if text:
                processed_text = self.post_process_text(text)
                print(f"Sau khi xử lý: {processed_text}")
                return processed_text
            return text
        except sr.RequestError as e:
            print(f"Không thể yêu cầu kết quả từ Google Speech Recognition; {e}")
            return None
        except sr.UnknownValueError:
            print("Google Speech Recognition không thể hiểu audio")
            return None
        except Exception as e:
            print(f"Lỗi trong quá trình nhận dạng giọng nói: {e}")
            return None
    
    def recognize_from_audio_file(self, audio_file_path):
        """
        Nhận dạng giọng nói từ file audio
        
        Args:
            audio_file_path: Đường dẫn đến file audio
        
        Returns:
            Văn bản nhận dạng từ giọng nói hoặc None nếu thất bại
        """
        try:
            # Đọc file audio
            with sr.AudioFile(audio_file_path) as source:
                # Thêm điều chỉnh nhiễu nền cho file audio
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # Thử nhận dạng với nhiều tùy chọn ngôn ngữ
            text = None
            try:
                # Nhận dạng bằng Google Speech Recognition
                text = self.recognizer.recognize_google(audio, language=self.language)
                print(f"Nhận dạng ban đầu: {text}")
            except sr.UnknownValueError:
                # Thử với tùy chọn ngôn ngữ khác
                try:
                    alt_language = "vi" if self.language == "vi-VN" else "vi-VN"
                    text = self.recognizer.recognize_google(audio, language=alt_language)
                    print(f"Nhận dạng với {alt_language}: {text}")
                except:
                    return None
            
            # Áp dụng hậu xử lý
            if text:
                processed_text = self.post_process_text(text)
                print(f"Sau khi xử lý: {processed_text}")
                return processed_text
            return None
        except Exception as e:
            print(f"Lỗi trong quá trình nhận dạng giọng nói từ file: {e}")
            return None
    
    def recognize_from_uploaded_file(self, uploaded_file, target_format="wav"):
        """
        Nhận dạng giọng nói từ file được tải lên Streamlit
        
        Args:
            uploaded_file: File audio được tải lên qua Streamlit
            target_format: Định dạng file audio
        
        Returns:
            Văn bản nhận dạng từ giọng nói hoặc None nếu thất bại
        """
        try:
            # Tạo file tạm thời để lưu file audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{target_format}") as tmp_file:
                tmp_file.write(uploaded_file.read())
                audio_path = tmp_file.name
            
            # Nhận dạng từ file
            text = self.recognize_from_audio_file(audio_path)
            
            # Xóa file tạm
            os.remove(audio_path)
            
            return text
        except Exception as e:
            print(f"Lỗi khi xử lý file tải lên: {e}")
            return None 