import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# API URL for tours
TOUR_API_URL = "https://tradivabe.felixtien.dev/api/Tour"

class TourAPI:
    """Class to handle API interactions for tour data"""
    
    def __init__(self, api_url: str = TOUR_API_URL):
        self.api_url = api_url
        
    def fetch_tours(self) -> List[Dict[str, Any]]:
        """
        Fetch all available tours from the API
        
        Returns:
            List of tour dictionaries
        """
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()  # Raise exception for bad status codes
            tours = response.json()
            print(f"✅ Successfully fetched {len(tours)} tours from API")
            return tours
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching tours from API: {e}")
            return []
    
    def search_tours(self, query: str, tours: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Search for tours based on the query
        
        Args:
            query: Search query string
            tours: Optional list of tours to search in (if None, will fetch from API)
            
        Returns:
            List of matching tour dictionaries
        """
        if tours is None:
            tours = self.fetch_tours()
        
        if not tours:
            return []
        
        # Lowercase the query for case-insensitive matching
        query = query.lower()
        
        # Search in title and description
        matched_tours = []
        for tour in tours:
            title = tour.get("title", "").lower() if tour.get("title") else ""
            description = tour.get("description", "").lower() if tour.get("description") else ""
            
            if query in title or query in description:
                matched_tours.append(tour)
        
        # Xử lý thêm thông tin cho mỗi tour
        processed_tours = [self.process_tour_info(tour) for tour in matched_tours]
        
        return processed_tours
    
    def recommend_tours(self, preferences: Dict[str, Any], tours: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Recommend tours based on preferences
        
        Args:
            preferences: Dictionary containing user preferences like:
                - location: preferred location name
                - max_price: maximum price per person
                - guests: number of guests
                - start_date: preferred start date (str in format YYYY-MM-DD)
                - days: preferred number of days
                - nights: preferred number of nights
            tours: Optional list of tours to filter (if None, will fetch from API)
            
        Returns:
            List of recommended tour dictionaries
        """
        if tours is None:
            tours = self.fetch_tours()
        
        if not tours:
            return []
        
        filtered_tours = tours.copy()
        
        # Filter by location if specified
        if preferences.get("location"):
            location_query = preferences["location"].lower()
            filtered_tours = [
                tour for tour in filtered_tours 
                if (tour.get("title") and location_query in tour["title"].lower()) or
                   (tour.get("description") and location_query in tour["description"].lower())
            ]
        
        # Filter by price if specified
        if preferences.get("max_price"):
            try:
                max_price = float(preferences["max_price"])
                filtered_tours = [
                    tour for tour in filtered_tours 
                    if tour.get("pricePerPerson") and float(tour["pricePerPerson"]) <= max_price
                ]
            except (ValueError, TypeError):
                pass  # Skip price filtering if conversion fails
        
        # Filter by guest capacity if specified
        if preferences.get("guests"):
            try:
                guests = int(preferences["guests"])
                filtered_tours = [
                    tour for tour in filtered_tours 
                    if tour.get("numberOfGuests") and tour["numberOfGuests"] >= guests
                ]
            except (ValueError, TypeError):
                pass  # Skip guest filtering if conversion fails
        
        # Filter by date if specified
        if preferences.get("start_date"):
            try:
                start_date = datetime.fromisoformat(preferences["start_date"])
                filtered_tours = [
                    tour for tour in filtered_tours 
                    if tour.get("dateStart") and datetime.fromisoformat(tour["dateStart"].split("T")[0]) >= start_date
                ]
            except (ValueError, TypeError):
                pass  # Skip date filtering if conversion fails
        
        # Xử lý thêm thông tin cho mỗi tour
        processed_tours = [self.process_tour_info(tour) for tour in filtered_tours]
        
        # Filter by days/nights if specified
        if preferences.get("days"):
            try:
                days = int(preferences["days"])
                processed_tours = [
                    tour for tour in processed_tours
                    if tour.get("calculatedDays") and tour["calculatedDays"] == days
                ]
            except (ValueError, TypeError):
                pass  # Skip days filtering if conversion fails
        
        if preferences.get("nights"):
            try:
                nights = int(preferences["nights"])
                processed_tours = [
                    tour for tour in processed_tours
                    if tour.get("calculatedNights") and tour["calculatedNights"] == nights
                ]
            except (ValueError, TypeError):
                pass  # Skip nights filtering if conversion fails
        
        # Sắp xếp tour theo độ phù hợp
        # - Ưu tiên số ngày đêm khớp với yêu cầu
        # - Tiếp theo là ngày bắt đầu sớm nhất
        def tour_sort_key(tour):
            days_match = 0
            nights_match = 0
            start_date_value = float('inf')  # Giá trị mặc định cao nếu không có ngày bắt đầu
            
            if preferences.get("days") and tour.get("calculatedDays"):
                days_match = 1 if tour["calculatedDays"] == preferences["days"] else 0
            
            if preferences.get("nights") and tour.get("calculatedNights"):
                nights_match = 1 if tour["calculatedNights"] == preferences["nights"] else 0
                
            if tour.get("dateStart"):
                try:
                    if isinstance(tour["dateStart"], str):
                        date_str = tour["dateStart"].split("T")[0]
                        start_date_value = datetime.fromisoformat(date_str).timestamp()
                except Exception:
                    pass
                    
            return (-days_match, -nights_match, start_date_value)
        
        # Sắp xếp tour theo tiêu chí
        processed_tours.sort(key=tour_sort_key)
        
        return processed_tours
    
    def process_tour_info(self, tour: Dict[str, Any]) -> Dict[str, Any]:
        """
        Xử lý và tính toán thêm thông tin cho tour
        
        Args:
            tour: Tour dictionary cần xử lý
            
        Returns:
            Tour dictionary đã được xử lý với thông tin bổ sung
        """
        processed_tour = tour.copy()
        
        # Tính số ngày và đêm từ dateStart và dateEnd
        if tour.get("dateStart") and tour.get("dateEnd"):
            try:
                # Xử lý chuỗi dateStart và dateEnd
                if isinstance(tour["dateStart"], str):
                    start_date = datetime.fromisoformat(tour["dateStart"].replace("Z", "+00:00"))
                else:
                    start_date = tour["dateStart"]
                
                if isinstance(tour["dateEnd"], str):
                    end_date = datetime.fromisoformat(tour["dateEnd"].replace("Z", "+00:00"))
                else:
                    end_date = tour["dateEnd"]
                
                # Tính số ngày giữa hai ngày (bao gồm cả ngày đầu và cuối)
                delta = end_date - start_date
                num_days = delta.days + 1
                
                # Tính số đêm (số ngày - 1, tối thiểu là 0)
                num_nights = max(0, num_days - 1)
                
                # Thêm thông tin vào tour
                processed_tour["calculatedDays"] = num_days
                processed_tour["calculatedNights"] = num_nights
                processed_tour["durationText"] = f"{num_days} ngày {num_nights} đêm"
                
                # Tính tổng giá nếu có pricePerPerson và numberOfGuests
                if tour.get("pricePerPerson") and tour.get("numberOfGuests"):
                    total_price = float(tour["pricePerPerson"]) * int(tour["numberOfGuests"])
                    processed_tour["calculatedTotalPrice"] = total_price
            except Exception as e:
                print(f"❌ Error calculating tour duration: {e}")
        
        return processed_tour
    
    def format_tour_message(self, tours: List[Dict[str, Any]], lang: str = "vi") -> str:
        """
        Format tours into a readable message
        
        Args:
            tours: List of tour dictionaries
            lang: Language code ("vi" for Vietnamese, "en" for English)
            
        Returns:
            Formatted message string
        """
        if not tours:
            return "Không tìm thấy tour phù hợp." if lang == "vi" else "No matching tours found."
        
        # Headers
        if lang == "vi":
            message = "## 🌟 Các tour du lịch phù hợp\n\n"
        else:
            message = "## 🌟 Matching Tours\n\n"
        
        # Add tour details
        for i, tour in enumerate(tours, 1):
            title = tour.get("title", "N/A")
            description = tour.get("description", "N/A")
            
            # Format price with correct commas
            price_per_person = tour.get('pricePerPerson', 0)
            if isinstance(price_per_person, str):
                try:
                    price_per_person = float(price_per_person)
                except (ValueError, TypeError):
                    price_per_person = 0
                    
            price = f"{price_per_person:,.0f} VND" if price_per_person else "N/A"
            
            # Format dates
            start_date = "N/A"
            end_date = "N/A"
            
            if tour.get("dateStart"):
                try:
                    start_date = datetime.fromisoformat(tour["dateStart"].replace("Z", "+00:00")).strftime("%d/%m/%Y")
                except (ValueError, TypeError):
                    pass
                    
            if tour.get("dateEnd"):
                try:
                    end_date = datetime.fromisoformat(tour["dateEnd"].replace("Z", "+00:00")).strftime("%d/%m/%Y")
                except (ValueError, TypeError):
                    pass
            
            # Thời gian tour
            duration_text = tour.get("durationText", "N/A")
            
            # Tổng giá tour
            total_price = tour.get('calculatedTotalPrice', 0)
            if isinstance(total_price, str):
                try:
                    total_price = float(total_price)
                except (ValueError, TypeError):
                    total_price = 0
                    
            total_price_text = f"{total_price:,.0f} VND" if total_price else "N/A"
            
            # Add to message
            message += f"### {i}. {title}\n\n"
            message += f"**Mô tả:** {description}\n\n" if lang == "vi" else f"**Description:** {description}\n\n"
            message += f"**Thời gian:** {duration_text}\n" if lang == "vi" else f"**Duration:** {duration_text}\n"
            message += f"**Giá/người:** {price}\n" if lang == "vi" else f"**Price/person:** {price}\n"
            message += f"**Tổng giá (dự kiến):** {total_price_text}\n" if lang == "vi" else f"**Total price (estimated):** {total_price_text}\n"
            message += f"**Ngày bắt đầu:** {start_date}\n" if lang == "vi" else f"**Start date:** {start_date}\n"
            message += f"**Ngày kết thúc:** {end_date}\n" if lang == "vi" else f"**End date:** {end_date}\n"
            message += f"**Số khách tối đa:** {tour.get('numberOfGuests', 'N/A')}\n\n" if lang == "vi" else f"**Max guests:** {tour.get('numberOfGuests', 'N/A')}\n\n"
        
        return message 