#!/usr/bin/env python3
"""
Vietnam Tourism Chatbot - Điểm vào chính
"""
import streamlit as st
import subprocess
import os
import sys

def main():
    """Hàm chính khởi chạy ứng dụng"""
    print("Khởi động Vietnam Tourism Chatbot...")
    
    # Kiểm tra môi trường và thư viện
    try:
        import streamlit
        import langchain
        print("✅ Các thư viện cần thiết đã được cài đặt")
    except ImportError as e:
        print(f"❌ Thiếu thư viện: {e}")
        print("Vui lòng cài đặt các thư viện cần thiết: pip install -r requirements.txt")
        sys.exit(1)
    
    # Kiểm tra file .env
    if not os.path.exists(".env"):
        print("⚠️ Không tìm thấy file .env")
        print("Tạo file .env mới...")
        with open(".env", "w") as f:
            f.write("GOOGLE_API_KEY=\n")
        print("Vui lòng cập nhật GOOGLE_API_KEY trong file .env")
    
    # Khởi chạy ứng dụng Streamlit
    try:
        subprocess.run(["streamlit", "run", "vietnam_tourism_app.py"])
    except Exception as e:
        print(f"❌ Lỗi khi khởi động ứng dụng: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 