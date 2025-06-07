#!/usr/bin/env python3
"""
Script để kiểm tra chi tiết các tài liệu đã tải
"""
from dotenv import load_dotenv
import os

def main():
    # Tải biến môi trường
    load_dotenv()
    
    # Kiểm tra API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found in environment variables.")
        exit(1)
        
    # Import sau khi kiểm tra môi trường
    from src.core.retriever import DocumentRetriever
    
    # Khởi tạo retriever
    print("\n🔍 Khởi tạo DocumentRetriever...\n")
    retriever = DocumentRetriever()
    
    # Tải trực tiếp tài liệu từ thư mục
    print("\n--- Tải tài liệu trực tiếp từ thư mục ---")
    docs = retriever.load_documents()
    print(f"Số lượng tài liệu đã tải: {len(docs)}")
    
    # In ra thông tin chi tiết về mỗi tài liệu
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown")
        print(f"\nDocument #{i+1}: {source}")
        preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
        print(f"Preview: {preview}")
    
    # Kiểm tra đặc biệt file TP. Hồ Chí Minh
    print("\n--- Kiểm tra đặc biệt file TP. Hồ Chí Minh ---")
    hcm_path = os.path.join("data", "vietnam_hochiminh.txt")
    if os.path.exists(hcm_path):
        try:
            with open(hcm_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"File TP. Hồ Chí Minh tồn tại, kích thước: {len(content)} ký tự")
                print(f"Preview: {content[:200]}...")
                
                # Kiểm tra xem có trong danh sách docs không
                found = False
                for doc in docs:
                    if doc.metadata.get("source") == hcm_path or doc.metadata.get("source") == "vietnam_hochiminh.txt":
                        found = True
                        break
                
                if found:
                    print("✅ File TP. Hồ Chí Minh được tìm thấy trong danh sách tài liệu đã tải")
                else:
                    print("❌ File TP. Hồ Chí Minh KHÔNG được tìm thấy trong danh sách tài liệu đã tải")
        except Exception as e:
            print(f"❌ Lỗi khi đọc file TP. Hồ Chí Minh: {e}")
    else:
        print(f"❌ File {hcm_path} không tồn tại")
    
    # Thử tìm kiếm trực tiếp về TP. Hồ Chí Minh
    print("\n--- Thử tìm kiếm về TP. Hồ Chí Minh ---")
    query = "TP. Hồ Chí Minh"
    docs = retriever.search_documents(query)
    print(f"Số lượng tài liệu tìm thấy: {len(docs)}")
    
    for i, doc in enumerate(docs):
        source = doc.metadata.get("source", "Unknown")
        print(f"\nKết quả #{i+1}: {source}")
        preview = doc.page_content[:100] + "..." if len(doc.page_content) > 100 else doc.page_content
        print(f"Preview: {preview}")

if __name__ == "__main__":
    main() 