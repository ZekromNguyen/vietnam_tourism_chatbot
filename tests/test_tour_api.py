#!/usr/bin/env python3
"""
Test cho module tour_api
"""
import unittest
import sys
import os
from datetime import datetime

# Thêm đường dẫn gốc vào sys.path để import các module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import module cần test
from src.api.tour_api import TourAPI

class TestTourAPI(unittest.TestCase):
    """Test cases cho TourAPI"""
    
    def setUp(self):
        """Thiết lập trước mỗi test"""
        self.tour_api = TourAPI()
        # Tạo dữ liệu mẫu để test
        self.sample_tours = [
            {
                "id": "1",
                "title": "Tour du lịch Đà Nẵng 3 ngày 2 đêm",
                "description": "Khám phá Đà Nẵng, Hội An, Bà Nà Hills",
                "pricePerPerson": 1500000,
                "numberOfGuests": 10,
                "dateStart": "2023-07-01T00:00:00Z",
                "dateEnd": "2023-07-03T00:00:00Z"
            },
            {
                "id": "2",
                "title": "Tour du lịch Hạ Long 2 ngày 1 đêm",
                "description": "Khám phá vịnh Hạ Long trên du thuyền",
                "pricePerPerson": 2000000,
                "numberOfGuests": 20,
                "dateStart": "2023-07-10T00:00:00Z",
                "dateEnd": "2023-07-11T00:00:00Z"
            },
            {
                "id": "3",
                "title": "Tour du lịch Phú Quốc 4 ngày 3 đêm",
                "description": "Khám phá đảo ngọc Phú Quốc",
                "pricePerPerson": 3000000,
                "numberOfGuests": 15,
                "dateStart": "2023-08-01T00:00:00Z",
                "dateEnd": "2023-08-04T00:00:00Z"
            }
        ]
    
    def test_search_tours(self):
        """Test hàm search_tours"""
        # Test tìm kiếm Đà Nẵng
        result = self.tour_api.search_tours("Đà Nẵng", self.sample_tours)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "1")
        
        # Test tìm kiếm Hạ Long
        result = self.tour_api.search_tours("Hạ Long", self.sample_tours)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "2")
        
        # Test tìm kiếm không có kết quả
        result = self.tour_api.search_tours("Sapa", self.sample_tours)
        self.assertEqual(len(result), 0)
    
    def test_recommend_tours(self):
        """Test hàm recommend_tours"""
        # Test recommend theo địa điểm
        preferences = {"location": "Đà Nẵng"}
        result = self.tour_api.recommend_tours(preferences, self.sample_tours)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "1")
        
        # Test recommend theo giá
        preferences = {"max_price": 2000000}
        result = self.tour_api.recommend_tours(preferences, self.sample_tours)
        self.assertEqual(len(result), 2)
        
        # Test recommend theo số lượng khách
        preferences = {"guests": 15}
        result = self.tour_api.recommend_tours(preferences, self.sample_tours)
        self.assertEqual(len(result), 2)
        
        # Test recommend theo ngày
        preferences = {"start_date": "2023-07-15"}
        result = self.tour_api.recommend_tours(preferences, self.sample_tours)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "3")
    
    def test_format_tour_message(self):
        """Test hàm format_tour_message"""
        # Test format message với danh sách tours
        result = self.tour_api.format_tour_message(self.sample_tours)
        self.assertIn("## 🌟 Các tour du lịch phù hợp", result)
        self.assertIn("Tour du lịch Đà Nẵng 3 ngày 2 đêm", result)
        self.assertIn("Tour du lịch Hạ Long 2 ngày 1 đêm", result)
        
        # Test format message với danh sách rỗng
        result = self.tour_api.format_tour_message([])
        self.assertEqual(result, "Không tìm thấy tour phù hợp.")
        
        # Test format message với ngôn ngữ tiếng Anh
        result = self.tour_api.format_tour_message(self.sample_tours, lang="en")
        self.assertIn("## 🌟 Matching Tours", result)

if __name__ == "__main__":
    unittest.main() 