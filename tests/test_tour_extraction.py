#!/usr/bin/env python3
"""
Test cho việc trích xuất thông tin tour từ truy vấn
"""
import unittest
import sys
import os
import re
from datetime import datetime

# Thêm đường dẫn gốc vào sys.path để import các module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestTourExtraction(unittest.TestCase):
    """Test cases cho việc trích xuất thông tin tour"""
    
    def setUp(self):
        """Thiết lập trước mỗi test"""
        # Import mã nguồn của hàm _parse_date và _parse_iso_date từ generator.py
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src', 'core', 'generator.py')
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tìm và lấy code của hàm _extract_tour_preferences
        extract_pattern = r'def _extract_tour_preferences\(self, query\):(.*?)def [^_]'
        extract_match = re.search(extract_pattern, content, re.DOTALL)
        extract_code = extract_match.group(1) if extract_match else ""
        
        # Tìm và lấy code của hàm _parse_date
        parse_date_pattern = r'def _parse_date\(self, date_str\):(.*?)def [^_]'
        parse_date_match = re.search(parse_date_pattern, content, re.DOTALL)
        parse_date_code = parse_date_match.group(1) if parse_date_match else ""
        
        # Tìm và lấy code của hàm _parse_iso_date
        parse_iso_date_pattern = r'def _parse_iso_date\(self, date_str\):(.*?)def [^_]'
        parse_iso_date_match = re.search(parse_iso_date_pattern, content, re.DOTALL)
        
        # Nếu không tìm thấy, thử tìm ở cuối file
        if not parse_iso_date_match:
            parse_iso_date_pattern = r'def _parse_iso_date\(self, date_str\):(.*)'
            parse_iso_date_match = re.search(parse_iso_date_pattern, content, re.DOTALL)
        
        parse_iso_date_code = parse_iso_date_match.group(1) if parse_iso_date_match else ""
        
        # Chuẩn bị mã nguồn cho class helper
        helper_code = f'''
class TourPreferencesExtractor:
    def _extract_tour_preferences(self, query):
{extract_code}
    
    def _parse_date(self, date_str):
{parse_date_code}
    
    def _parse_iso_date(self, date_str):
{parse_iso_date_code}
'''
        
        # Thực thi mã nguồn để tạo class
        exec(helper_code, globals())
        
        # Tạo instance
        self.extractor = TourPreferencesExtractor()
    
    def test_extract_location(self):
        """Test trích xuất địa điểm"""
        # Test với câu hỏi đơn giản
        query = "Tôi muốn đi du lịch Đà Nẵng"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("location"), "du lịch Đà Nẵng")
        
        # Test với câu hỏi phức tạp hơn
        query = "Tìm cho tôi tour đi Hạ Long 3 ngày 2 đêm"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("location"), "Hạ Long")
        
        # Test với địa điểm có dấu
        query = "Tôi muốn đi Phú Quốc vào tháng sau"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("location"), "Phú Quốc vào tháng sau")
    
    def test_extract_price(self):
        """Test trích xuất giá tiền"""
        # Test với đơn vị triệu
        query = "Tìm tour đi Đà Lạt dưới 5 triệu"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("max_price"), 5000000)
        
        # Test với số nhỏ (giả định là triệu)
        query = "Tôi muốn tìm tour Hà Nội với giá 3tr"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("max_price"), 3000000)
        
        # Test với số lớn
        query = "Tìm tour Sapa giá không quá 4500000 đồng"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("max_price"), 4500000)
    
    def test_extract_guests(self):
        """Test trích xuất số lượng khách"""
        # Test với số
        query = "Tour Đà Nẵng cho 4 người"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("guests"), 4)
        
        # Test với chữ
        query = "Tìm tour Nha Trang cho hai người"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("guests"), 2)
    
    def test_extract_duration(self):
        """Test trích xuất thời gian"""
        # Test với ngày và đêm
        query = "Tour Đà Nẵng 3 ngày 2 đêm"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("days"), 3)
        self.assertEqual(preferences.get("nights"), 2)
        
        # Test chỉ với ngày
        query = "Tìm tour Hà Nội 2 ngày"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("days"), 2)
        self.assertEqual(preferences.get("nights"), 1)  # Tự suy ra từ số ngày
        
        # Test chỉ với đêm
        query = "Tour Phú Quốc 3 đêm"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("nights"), 3)
        self.assertEqual(preferences.get("days"), 4)  # Tự suy ra từ số đêm
    
    def test_extract_dates(self):
        """Test trích xuất ngày tháng"""
        # Test với ngày bắt đầu và kết thúc
        today = datetime.now()
        year = today.year
        
        # Format DD/MM
        query = "Tour từ ngày 15/06 đến ngày 20/06"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("start_date"), f"{year}-06-15")
        self.assertEqual(preferences.get("end_date"), f"{year}-06-20")
        self.assertEqual(preferences.get("days"), 6)  # 15 đến 20 là 6 ngày
        self.assertEqual(preferences.get("nights"), 5)  # 6 ngày 5 đêm
        
        # Format DD-MM-YYYY
        query = "Tour từ ngày 10-07-2025 đến 15-07-2025"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("start_date"), "2025-07-10")
        self.assertEqual(preferences.get("end_date"), "2025-07-15")
        
        # Chỉ có ngày bắt đầu
        query = "Tour bắt đầu ngày 20/12"
        preferences = self.extractor._extract_tour_preferences(query)
        self.assertEqual(preferences.get("start_date"), f"{year}-12-20")
    
    def test_complex_query(self):
        """Test với câu truy vấn phức tạp"""
        query = "Tìm tour du lịch Đà Nẵng 4 ngày 3 đêm từ ngày 10/07 đến 13/07 cho 2 người với giá dưới 6 triệu"
        preferences = self.extractor._extract_tour_preferences(query)
        
        self.assertEqual(preferences.get("location"), "Đà Nẵng")
        self.assertEqual(preferences.get("days"), 4)
        self.assertEqual(preferences.get("nights"), 3)
        self.assertEqual(preferences.get("start_date"), f"{datetime.now().year}-07-10")
        self.assertEqual(preferences.get("end_date"), f"{datetime.now().year}-07-13")
        self.assertEqual(preferences.get("guests"), 2)
        self.assertEqual(preferences.get("max_price"), 6000000)
    
    def test_dateStart_dateEnd_extraction(self):
        """Test với cấu trúc giống JSON API"""
        query = """Tôi muốn đặt tour với thông tin:
        {
            "title": "Tây Ninh 3 ngày 1 đêm",
            "dateStart": "2025-06-03T09:25:00.592",
            "dateEnd": "2025-06-05T09:25:00.592",
            "numberOfGuests": 3,
            "pricePerPerson": 1000000
        }"""
        preferences = self.extractor._extract_tour_preferences(query)
        
        # Kiểm tra xem có trích xuất được dateStart và dateEnd không
        self.assertIsNotNone(preferences.get("start_date"))
        self.assertIsNotNone(preferences.get("end_date"))
        
        # Kiểm tra số ngày và đêm
        self.assertEqual(preferences.get("days"), 3)  # 3/6 đến 5/6 là 3 ngày
        self.assertEqual(preferences.get("nights"), 2)  # 3 ngày 2 đêm
        
        # Kiểm tra giá
        self.assertEqual(preferences.get("max_price"), 1000000)
        
        # Kiểm tra số lượng khách
        self.assertEqual(preferences.get("guests"), 3)

    def test_special_format_query(self):
        """Test với định dạng đặc biệt nêu trong ví dụ"""
        query = "Tìm một tour du lịch 3 ngày 2 đêm với giá 2000 đồng một người ở vũng tàu"
        preferences = self.extractor._extract_tour_preferences(query)
        
        # Kiểm tra số ngày và đêm
        self.assertEqual(preferences.get("days"), 3)
        self.assertEqual(preferences.get("nights"), 2)
        
        # Kiểm tra giá
        self.assertEqual(preferences.get("max_price"), 2000)
        
        # Kiểm tra địa điểm
        self.assertIsNotNone(preferences.get("location"))
        self.assertIn("vũng tàu", preferences.get("location").lower())

    def test_million_price_extraction(self):
        """Test trích xuất giá tiền ở định dạng triệu"""
        # Test với từ "triệu" rõ ràng
        query = "tìm cho tôi tour du lịch 1 ngày 1 đêm giá 2 triệu ở vũng tàu"
        preferences = self.extractor._extract_tour_preferences(query)
        
        # Kiểm tra số ngày và đêm
        self.assertEqual(preferences.get("days"), 1)
        self.assertEqual(preferences.get("nights"), 1)
        
        # Kiểm tra giá (2 triệu = 2.000.000)
        self.assertEqual(preferences.get("max_price"), 2000000)
        
        # Kiểm tra địa điểm
        self.assertIsNotNone(preferences.get("location"))
        self.assertIn("vũng tàu", preferences.get("location").lower())

if __name__ == "__main__":
    unittest.main()