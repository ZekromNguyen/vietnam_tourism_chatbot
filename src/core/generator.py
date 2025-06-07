# Import necessary Gemini components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain # Keep this for Gemini as well
# Import prompt templates
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import os
import warnings
import re
from src.api.tour_api import TourAPI
from datetime import datetime

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# --- Define the Persona System Prompt ---
# --- Persona System Prompt ---
# Updated to explicitly request Vietnamese responses
VIETNAM_ATTRACTIONS_PROMPT = """
Bạn là một hướng dẫn viên du lịch Việt Nam am hiểu và thân thiện.
Vai trò của bạn là cung cấp thông tin chi tiết, hấp dẫn và hữu ích về các điểm du lịch, văn hóa, ẩm thực và lời khuyên du lịch tại Việt Nam dựa trên ngữ cảnh được cung cấp.
Hãy luôn duy trì giọng điệu nồng nhiệt, tôn trọng và nhiệt tình.
Tránh bịa đặt thông tin không có trong ngữ cảnh. Nếu không tìm thấy câu trả lời trong ngữ cảnh, hãy nói rằng bạn không có thông tin đó.

Bạn cũng có khả năng tìm kiếm và đề xuất các tour du lịch dựa trên yêu cầu của người dùng. Khi người dùng hỏi về tour du lịch, hãy cố gắng xác định:
1. Điểm đến họ muốn đến
2. Số lượng khách
3. Ngân sách (nếu có)
4. Thời gian họ muốn đi

Đặc biệt chú ý đến thông tin về các thành phố lớn: Hà Nội, Huế, TP. Hồ Chí Minh (Sài Gòn). Bạn có dữ liệu cập nhật và chi tiết về các thành phố này, vì vậy hãy ưu tiên sử dụng thông tin này khi người dùng hỏi về chúng.

**Quan trọng: Hãy luôn trả lời bằng tiếng Việt.**

Respond helpfully based on the provided context, your persona, and the chat history.
"""
# --- End of Persona System Prompt ---

class ResponseGenerator:
    def __init__(self, retriever, model_name="gemini-1.5-flash"):
        self.retriever = retriever
        self.model_name = model_name
        self.tour_api = TourAPI()  # Initialize the tour API

        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")

        try:
            self.llm = ChatGoogleGenerativeAI(model=self.model_name,
                                              temperature=0.7,
                                              convert_system_message_to_human=True) # Still useful for some chain types
            print(f"Initialized Google Gemini LLM: {self.model_name}")
        except Exception as e:
            print(f"Error initializing Google Gemini LLM: {e}")
            raise e

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key='answer' # Ensure memory output key matches chain output key
        )

        self.chain = self._create_chain()

    def _create_chain(self):
        """Create a conversational chain with retrieval capabilities and the specific persona"""
        if not self.retriever.vector_store:
             # Attempt to create vector store if not already done (e.g., during init)
             print("Retriever vector store not found, attempting creation...")
             self.retriever.create_vector_store()
             if not self.retriever.vector_store:
                 print("Failed to create vector store for chain initialization.")
                 return None

        # Define the prompt structure for the LLM call within the chain
        # This prompt template incorporates the system message, history, context, and question
        condense_question_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", VIETNAM_ATTRACTIONS_PROMPT), # Inject the persona here
                ("human", "Chat History:\n{chat_history}\n\nFollow Up Input: {question}\nRetrieved Context:\n{context}\n\nBased on the context and chat history, answer the follow up input adhering strictly to your defined role and scope:"),
            ]
        )


        try:
            # Create the ConversationalRetrievalChain
            # Pass the custom prompt to the combine_docs_chain
            chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.retriever.vector_store.as_retriever(),
                memory=self.memory,
                # Key change: Pass the custom prompt template here
                combine_docs_chain_kwargs={"prompt": condense_question_prompt},
                return_source_documents=True, # Keep this if you want to see sources
                verbose=False # Set to True for debugging chain steps
            )
            print("ConversationalRetrievalChain created successfully with custom prompt.")
            return chain
        except Exception as e:
            print(f"Error creating ConversationalRetrievalChain for Gemini: {e}")
            return None
    
    def _is_tour_query(self, query):
        """Kiểm tra xem câu hỏi có phải là về tour hay không"""
        # Các từ khóa chính để xác định đây là câu hỏi về tour
        primary_tour_patterns = [
            r'tour',
            r'chuyến đi',
            r'phượt'
        ]
        
        # Các từ khóa phụ có thể kết hợp với ngữ cảnh để xác định là câu hỏi về tour
        secondary_tour_patterns = [
            r'du lịch'
        ]
        
        # Ngữ cảnh thể hiện người dùng đang hỏi về tour cụ thể
        tour_context_patterns = [
            r'tìm',
            r'gợi ý',
            r'đề xuất',
            r'giá',
            r'chi phí',
            r'đặt',
            r'book',
            r'tham quan',
            r'khám phá',
            r'ngày',
            r'đêm',
            r'lịch trình',
            r'người'
        ]
        
        # Convert query to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # Nếu có từ khóa chính, đây là câu hỏi về tour
        for pattern in primary_tour_patterns:
            if re.search(pattern, query_lower):
                return True
        
        # Nếu có từ khóa phụ và kết hợp với ngữ cảnh, đây là câu hỏi về tour
        for pattern in secondary_tour_patterns:
            if re.search(pattern, query_lower):
                # Kiểm tra thêm ngữ cảnh
                for context in tour_context_patterns:
                    if re.search(context, query_lower):
                        return True
        
        return False
    
    def _extract_tour_preferences(self, query):
        """Extract tour preferences from the query"""
        # Initialize preferences
        preferences = {}
        
        # Extract location
        location_patterns = [
            r'(?:đến|tới|ở|tại|về|đi) ([A-Za-zÀ-ỹ]+(?:\s+[A-Za-zÀ-ỹ]+)*)',
            r'tour (?:đi |du lịch )?([A-Za-zÀ-ỹ]+(?:\s+[A-Za-zÀ-ỹ]+)*)',
            r'du lịch ([A-Za-zÀ-ỹ]+(?:\s+[A-Za-zÀ-ỹ]+)*)',
            r'ở ([A-Za-zÀ-ỹ]+(?:\s+[A-Za-zÀ-ỹ]+)*)'
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                for match in matches:
                    # Clean up the location
                    location = match.strip()
                    # Lọc bỏ các từ không phải địa điểm
                    location_words = location.split()
                    if len(location_words) > 0 and any(word in ["với", "cho", "và", "giá", "dưới"] for word in location_words):
                        # Cắt chuỗi tại từ đầu tiên là "với", "cho", "và", "giá", "dưới"
                        for i, word in enumerate(location_words):
                            if word in ["với", "cho", "và", "giá", "dưới"]:
                                location = " ".join(location_words[:i])
                                break
                    
                    if location and len(location) > 2:  # Avoid too short matches
                        preferences["location"] = location
                        break
                if "location" in preferences:
                    break
        
        # Extract price
        price_patterns = [
            r'giá (\d+[,.]?\d*)',
            r'(\d+[,.]?\d*)[k\s]+(đồng|vnd)',
            r'dưới (\d+[,.]?\d*)',
            r'không quá (\d+[,.]?\d*)',
            r'tối đa (\d+[,.]?\d*)',
            r'(\d+[,.]?\d*)\s*(triệu|tr)',
            r'pricePerPerson[:\s]+(\d+[,.]?\d*)',
            r'"pricePerPerson"[:\s]+(\d+[,.]?\d*)',
            r'giá (\d+[,.]?\d*)[^A-Za-zÀ-ỹ]',
            r'(\d+[,.]?\d*)\s*đồng\s+một\s+người'
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                try:
                    # Extract the first group match and convert to float
                    price_str = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    price = float(price_str.replace(',', '').replace('.', ''))
                    
                    # If price is too small, assume it's in millions
                    if price < 1000 and ("triệu" in query or "tr" in query.lower()):
                        price *= 1000000
                    elif "triệu" in query or "tr" in query.lower():
                        # Giá được chỉ định trong đơn vị triệu
                        price *= 1000000
                    
                    preferences["max_price"] = price
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract number of guests
        guest_patterns = [
            r'(\d+)\s+(người|khách)',
            r'(một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)\s+(người|khách)',
            r'numberOfGuests[:\s]+(\d+)',
            r'"numberOfGuests"[:\s]+(\d+)'
        ]
        
        number_words = {
            'một': 1, 'hai': 2, 'ba': 3, 'bốn': 4, 'năm': 5,
            'sáu': 6, 'bảy': 7, 'tám': 8, 'chín': 9, 'mười': 10
        }
        
        for pattern in guest_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                try:
                    guest_str = matches[0][0] if isinstance(matches[0], tuple) else matches[0]
                    
                    # Convert word to number if needed
                    if guest_str.lower() in number_words:
                        guests = number_words[guest_str.lower()]
                    else:
                        guests = int(guest_str)
                    
                    preferences["guests"] = guests
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract days and nights
        duration_patterns = [
            r'(\d+)\s+ngày\s+(\d+)\s+đêm',
            r'(\d+)\s+ngày',
            r'(\d+)\s+đêm',
            r'tour\s+(?:du\s+lịch\s+)?(?:[A-Za-zÀ-ỹ]+(?:\s+[A-Za-zÀ-ỹ]+)*\s+)?(\d+)\s+ngày\s+(\d+)\s+đêm'
        ]
        
        for pattern in duration_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                try:
                    if len(matches[0]) == 2:  # ngày + đêm
                        days = int(matches[0][0])
                        nights = int(matches[0][1])
                        preferences["days"] = days
                        preferences["nights"] = nights
                    else:  # chỉ ngày hoặc chỉ đêm
                        value = int(matches[0])
                        if "ngày" in pattern:
                            preferences["days"] = value
                            preferences["nights"] = max(0, value - 1)  # Giả định số đêm
                        else:
                            preferences["nights"] = value
                            preferences["days"] = value + 1  # Giả định số ngày
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract date range (ngày bắt đầu và kết thúc)
        date_patterns = [
            r'từ\s+ngày\s+(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\s+(?:đến|tới)\s+(?:ngày\s+)?(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)',
            r'(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)\s+(?:đến|tới)\s+(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)',
            r'(?:ngày|date)\s+(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)',
            r'dateStart[:\s]+"?([^",\s]+)',
            r'"?dateStart"?[:\s]+"?([^",\s]+)',
            r'dateEnd[:\s]+"?([^",\s]+)',
            r'"?dateEnd"?[:\s]+"?([^",\s]+)'
        ]
        
        # Dùng cho API format
        extracted_dates = {}
        
        for pattern in date_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                try:
                    # Kiểm tra xem có phải mẫu có dateStart/dateEnd không
                    if "dateStart" in pattern:
                        date_str = matches[0]
                        date_obj = self._parse_iso_date(date_str)
                        if date_obj:
                            extracted_dates["start_date"] = date_obj
                    elif "dateEnd" in pattern:
                        date_str = matches[0]
                        date_obj = self._parse_iso_date(date_str)
                        if date_obj:
                            extracted_dates["end_date"] = date_obj
                    # Xử lý các định dạng ngày khác nhau
                    elif len(matches[0]) == 2:  # Có cả ngày bắt đầu và kết thúc
                        start_date_str = matches[0][0]
                        end_date_str = matches[0][1]
                        
                        # Chuyển đổi chuỗi ngày thành đối tượng datetime
                        start_date = self._parse_date(start_date_str)
                        end_date = self._parse_date(end_date_str)
                        
                        if start_date and end_date:
                            extracted_dates["start_date"] = start_date
                            extracted_dates["end_date"] = end_date
                    else:  # Chỉ có một ngày
                        date_str = matches[0]
                        date_obj = self._parse_date(date_str)
                        if date_obj:
                            extracted_dates["start_date"] = date_obj
                except (ValueError, IndexError) as e:
                    print(f"Error parsing date: {e}")
                    pass
        
        # Nếu có cả ngày bắt đầu và kết thúc, tính số ngày và đêm
        if "start_date" in extracted_dates and "end_date" in extracted_dates:
            start_date = extracted_dates["start_date"]
            end_date = extracted_dates["end_date"]
            
            # Tính số ngày giữa hai ngày (bao gồm cả ngày đầu và cuối)
            delta = (end_date - start_date).days + 1
            preferences["days"] = delta
            preferences["nights"] = max(0, delta - 1)
            
            # Format lại ngày tháng để trả về
            preferences["start_date"] = start_date.strftime("%Y-%m-%d")
            preferences["end_date"] = end_date.strftime("%Y-%m-%d")
        elif "start_date" in extracted_dates:
            preferences["start_date"] = extracted_dates["start_date"].strftime("%Y-%m-%d")
        
        return preferences
    
    def _parse_date(self, date_str):
        """
        Phân tích chuỗi ngày thành đối tượng datetime
        
        Args:
            date_str: Chuỗi ngày cần phân tích
            
        Returns:
            Đối tượng datetime hoặc None nếu không thể phân tích
        """
        try:
            # Xử lý các định dạng khác nhau (DD/MM/YYYY, DD-MM-YYYY, DD/MM, DD-MM)
            formats = ["%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y", "%d/%m", "%d-%m"]
            
            for fmt in formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    # Nếu không có năm, sử dụng năm hiện tại
                    if fmt in ["%d/%m", "%d-%m"]:
                        current_year = datetime.now().year
                        date_obj = date_obj.replace(year=current_year)
                    return date_obj
                except ValueError:
                    continue
            
            return None
        except Exception as e:
            print(f"Error parsing date '{date_str}': {e}")
            return None
    
    def _parse_iso_date(self, date_str):
        """
        Phân tích chuỗi ngày định dạng ISO thành đối tượng datetime
        
        Args:
            date_str: Chuỗi ngày ISO cần phân tích (YYYY-MM-DDThh:mm:ss...)
            
        Returns:
            Đối tượng datetime hoặc None nếu không thể phân tích
        """
        try:
            # Xử lý chuỗi ISO-format (có thể có phần milisecond hoặc timezone)
            if 'T' in date_str:
                # Đây là định dạng ISO với giờ phút giây
                # Xử lý các trường hợp không có 'Z' hoặc offset timezone
                clean_date_str = date_str.replace('Z', '+00:00')
                if '+' not in clean_date_str and '-' not in clean_date_str[10:]:
                    clean_date_str += '+00:00'
                
                date_obj = datetime.fromisoformat(clean_date_str)
                return date_obj
            else:
                # Nếu chỉ có phần ngày YYYY-MM-DD
                date_obj = datetime.fromisoformat(date_str)
                return date_obj
        except Exception as e:
            print(f"Error parsing ISO date '{date_str}': {e}")
            return None

    def generate_response(self, query):
        """Generate a response for the user query using Gemini and the defined persona"""
        # Check if this is a tour-related query
        if self._is_tour_query(query):
            print("Detected tour query, processing with Tour API...")
            preferences = self._extract_tour_preferences(query)
            print(f"Extracted preferences: {preferences}")
            
            # Kiểm tra xem có đủ thông tin để tìm tour hay không
            if not preferences:
                print("No preferences extracted, continuing with normal response")
                # Không có thông tin, nhưng vẫn là câu hỏi về tour - sử dụng câu trả lời thông thường
                pass
            else:
                # Get matching tours based on preferences
                try:
                    matching_tours = self.tour_api.recommend_tours(preferences)
                    print(f"Found {len(matching_tours)} matching tours")
                    
                    if matching_tours:
                        # If we have matching tours, format them and return
                        tour_message = self.tour_api.format_tour_message(matching_tours)
                        
                        # Add a message from the LLM to introduce the tours
                        try:
                            intro_prompt = f"""
                            Tôi đã tìm thấy một số tour du lịch phù hợp với yêu cầu "{query}" của bạn.
                            Hãy viết một đoạn văn ngắn (2-3 câu) để giới thiệu những tour này.
                            Hãy đảm bảo lời giới thiệu phù hợp với vai trò hướng dẫn viên du lịch Việt Nam thân thiện.
                            """
                            intro_response = self.llm.invoke(intro_prompt)
                            intro_text = intro_response.content
                            
                            # Combine intro and tour details
                            return f"{intro_text}\n\n{tour_message}"
                        except Exception as e:
                            print(f"Error generating intro: {e}")
                            # Fallback to just returning the tour message
                            return tour_message
                    else:
                        # Không tìm thấy tour phù hợp, thông báo cho người dùng
                        try:
                            no_tour_prompt = f"""
                            Tôi đã tìm kiếm nhưng không thấy tour nào phù hợp với yêu cầu "{query}" của bạn.
                            Hãy viết một đoạn văn ngắn (2-3 câu) thông báo không tìm thấy tour và gợi ý cho người dùng thử tìm kiếm theo cách khác.
                            Hãy đảm bảo lời giới thiệu phù hợp với vai trò hướng dẫn viên du lịch Việt Nam thân thiện.
                            """
                            no_tour_response = self.llm.invoke(no_tour_prompt)
                            return no_tour_response.content
                        except Exception as e:
                            print(f"Error generating no tour message: {e}")
                            # Fallback to a simple message
                            return "Xin lỗi, tôi không tìm thấy tour nào phù hợp với yêu cầu của bạn. Bạn có thể thử tìm kiếm với địa điểm khác hoặc với ngân sách khác không?"
                except Exception as e:
                    print(f"Error during tour recommendation: {e}")
                    # Tiếp tục với câu trả lời thông thường
        
        # If not a tour query or no matching tours, use the regular chain
        if not self.chain:
            return "Error: The conversational chain is not initialized. Cannot generate response."

        try:
            # Invoke the chain. It handles history, retrieval, and prompting internally.
            response = self.chain.invoke({"question": query})
            # print(f"Chain response: {response}") # Debugging output
            return response.get("answer", "Sorry, I encountered an issue generating a response.")
        except Exception as e:
            print(f"Error during Gemini response generation: {e}")
            # Check for specific API errors if needed
            if "API key not valid" in str(e):
                 return "Error: Invalid Google API Key. Please check your .env file."
            return f"I encountered an error processing your query. Please try again. (Error: {str(e)[:100]}...)"