class VoiceRecognition:
    def __init__(self, language="vi-VN"):
        """
        Phiên bản dự phòng cho nhận dạng giọng nói (không sử dụng microphone)
        
        Args:
            language: Ngôn ngữ nhận dạng (mặc định: Tiếng Việt)
        """
        self.language = language
        print("Đang sử dụng VoiceRecognition dự phòng (không có microphone)")
    
    def recognize_from_microphone(self, timeout=5):
        """
        Giả lập nhận dạng giọng nói từ microphone
        
        Args:
            timeout: Thời gian ghi âm tối đa (giây)
        
        Returns:
            None để thông báo cần cài đặt thêm thư viện
        """
        print("Chức năng microphone không khả dụng.")
        print("Vui lòng cài đặt đầy đủ SpeechRecognition và PyAudio")
        return None
    
    def recognize_from_audio_file(self, audio_file_path):
        """
        Giả lập nhận dạng giọng nói từ file audio
        
        Args:
            audio_file_path: Đường dẫn đến file audio
        
        Returns:
            None vì chức năng không khả dụng
        """
        print("Chức năng nhận dạng từ file audio không khả dụng")
        return None
    
    def recognize_from_uploaded_file(self, uploaded_file, target_format="wav"):
        """
        Giả lập nhận dạng giọng nói từ file được tải lên
        
        Args:
            uploaded_file: File audio được tải lên qua Streamlit
            target_format: Định dạng file audio
        
        Returns:
            None vì chức năng không khả dụng
        """
        print("Chức năng nhận dạng từ file tải lên không khả dụng")
        return None 