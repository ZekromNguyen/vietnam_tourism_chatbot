from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader
# Import Google Embeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import sys # Import sys for potential critical exits
from langchain.schema import Document # Keep this for manual loading
from typing import List, Optional # Add type hints for clarity
import re  # Thêm thư viện re để sử dụng regex

# --- Constants ---
DEFAULT_DATA_DIR = "data"
GOOGLE_EMBEDDING_MODEL = "models/embedding-001"
TEXT_CHUNK_SIZE = 1000
TEXT_CHUNK_OVERLAP = 200
SEARCH_K = 4 # Default number of documents to retrieve

class DocumentRetriever:
    # Add type hints to __init__
    def __init__(self, data_dir: str = DEFAULT_DATA_DIR):
        self.data_dir = data_dir
        print(f"ℹ️ DocumentRetriever initialized with data directory: '{self.data_dir}'")

        # Validate Google API Key early
        if not os.getenv("GOOGLE_API_KEY"):
             print("❌ Error: GOOGLE_API_KEY not found in environment variables.")
             # Consider raising a more specific error or handling it based on application needs
             raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        else:
            print("✅ GOOGLE_API_KEY found.")

        # Initialize embeddings
        self.embedding_model_name = GOOGLE_EMBEDDING_MODEL
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(model=self.embedding_model_name)
            print(f"✅ Google Embeddings initialized with model: '{self.embedding_model_name}'")
        except Exception as e:
            print(f"❌ Error initializing Google Embeddings: {e}")
            # Depending on the app, you might want to raise the error or handle it
            raise RuntimeError(f"Failed to initialize Google Embeddings: {e}") from e

        self.vector_store: Optional[FAISS] = None # Initialize vector_store with type hint

    # Add type hints
    def load_documents(self) -> List[Document]:
        """Load documents from the data directory using DirectoryLoader."""
        if not os.path.exists(self.data_dir):
            print(f"⚠️ Warning: Data directory '{self.data_dir}' does not exist.")
            return []

        print(f"ℹ️ Attempting to load documents from '{self.data_dir}' using DirectoryLoader...")
        try:
            # Using TextLoader with UTF-8 encoding
            loader = DirectoryLoader(
                self.data_dir,
                glob="**/*.txt", # Ensure this pattern matches your files
                loader_cls=lambda file_path: TextLoader(file_path, encoding="utf-8"),
                show_progress=True, # Optional: show progress
                # Use recursive=True if documents are in subdirectories
                recursive=True
            )
            documents = loader.load()
            if documents:
                print(f"✅ Successfully loaded {len(documents)} documents using DirectoryLoader.")
            else:
                print(f"ℹ️ DirectoryLoader found no .txt files matching the pattern in '{self.data_dir}'.")
            return documents
        except Exception as e:
            print(f"❌ Error loading documents using DirectoryLoader: {e}")
            # Optionally log the full traceback for debugging
            # import traceback
            # print(traceback.format_exc())
            return [] # Return empty list on error

    # Add type hints
    def load_documents_manually(self) -> List[Document]:
        """Load documents manually, iterating through files in the data directory."""
        documents = []
        if not os.path.exists(self.data_dir):
            # This case is already handled by the calling function, but good for standalone use
            print(f"⚠️ Warning: Data directory '{self.data_dir}' does not exist.")
            return documents

        print(f"ℹ️ Attempting to load documents manually from '{self.data_dir}'...")
        loaded_count = 0
        error_count = 0
        try:
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.txt'):
                    file_path = os.path.join(self.data_dir, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if content.strip(): # Ensure content is not just whitespace
                            doc = Document(
                                page_content=content,
                                metadata={"source": file_path} # Use filename as source
                            )
                            documents.append(doc)
                            loaded_count += 1
                        else:
                            print(f"⚠️ Skipping empty file: {filename}")
                    except Exception as e:
                        print(f"❌ Error loading file '{file_path}' manually: {e}")
                        error_count += 1

            if loaded_count > 0:
                print(f"✅ Manually loaded {loaded_count} documents.")
            if error_count > 0:
                print(f"⚠️ Encountered errors loading {error_count} files manually.")
            if loaded_count == 0 and error_count == 0:
                 print(f"ℹ️ No .txt files found or loaded manually in '{self.data_dir}'.")

            return documents
        except Exception as e:
            print(f"❌ Error during manual document loading process: {e}")
            return [] # Return empty list on error

    # Add type hints
    def create_vector_store(self) -> Optional[FAISS]:
        """Create or retrieve the FAISS vector store from loaded documents."""
        # Check if already created
        if self.vector_store:
            print("ℹ️ Vector store already exists.")
            return self.vector_store

        print("--- Starting Vector Store Creation ---")
        # Try DirectoryLoader first
        documents = self.load_documents()
        # If DirectoryLoader fails or finds nothing, try manual loading
        if not documents:
             print("ℹ️ DirectoryLoader yielded no documents, attempting manual loading...")
             documents = self.load_documents_manually()

        # If still no documents, abort
        if not documents:
            print("❌ Error: No documents found after attempting both loading methods.")
            print(f"Ensure .txt files are present in '{self.data_dir}'.")
            self.vector_store = None # Explicitly set to None
            print("--- Vector Store Creation Failed ---")
            return None

        # Split documents
        print(f"ℹ️ Splitting {len(documents)} documents into chunks (size={TEXT_CHUNK_SIZE}, overlap={TEXT_CHUNK_OVERLAP})...")
        try:
            text_splitter = CharacterTextSplitter(
                chunk_size=TEXT_CHUNK_SIZE,
                chunk_overlap=TEXT_CHUNK_OVERLAP,
                separator="\n" # Common separator, adjust if needed
            )
            texts = text_splitter.split_documents(documents)
        except Exception as e:
             print(f"❌ Error splitting documents: {e}")
             print("--- Vector Store Creation Failed ---")
             return None


        if not texts:
             print("❌ Error: Failed to split documents into text chunks (result was empty).")
             print("--- Vector Store Creation Failed ---")
             return None
        print(f"✅ Successfully split documents into {len(texts)} text chunks.")

        # Create FAISS index
        print(f"ℹ️ Creating FAISS vector store with {len(texts)} chunks using '{self.embedding_model_name}'...")
        try:
            vector_store = FAISS.from_documents(texts, self.embeddings)
            self.vector_store = vector_store # Store the created vector store
            print("✅ FAISS vector store created successfully.")
            print("--- Vector Store Creation Finished ---")
            return vector_store
        except Exception as e:
            print(f"❌ Error creating FAISS vector store: {e}")
            # Check for common API key issues
            if "API key not valid" in str(e) or "permission" in str(e).lower():
                 print("‼️ Hint: Check if your GOOGLE_API_KEY is correct and has the necessary permissions for the embedding model.")
            self.vector_store = None # Ensure it's None on failure
            print("--- Vector Store Creation Failed ---")
            return None

    # Add type hints
    def search_documents(self, query: str, k: int = SEARCH_K) -> List[Document]:
        """Search for documents related to the query using the vector store."""
        print(f"\n--- Performing Search for query: '{query}' (k={k}) ---")
        # Ensure vector store exists, try creating if not
        if not self.vector_store:
            print("⚠️ Vector store not initialized. Attempting to create it now...")
            self.create_vector_store()
            # If creation failed, return empty list
            if not self.vector_store:
                 print("❌ Error: Failed to create vector store for search. Cannot perform search.")
                 print("--- Search Failed ---")
                 return []

        # Kiểm tra xem query có liên quan đến các thành phố không
        city_patterns = {
            "hcm": r'(hồ\s*chí\s*minh|sài\s*gòn|tp\s*hcm|tp\.?\s*hồ\s*chí\s*minh)',
            "hanoi": r'(hà\s*nội|hà\s*thành)',
            "hue": r'(huế|cố\s*đô)',
            "danang": r'(đà\s*nẵng)',
            "vungtau": r'(vũng\s*tàu|bà\s*rịa|bãi\s*sau|bãi\s*trước)'
        }
        
        # Tìm thành phố trong query
        city_match = None
        for city, pattern in city_patterns.items():
            if re.search(pattern, query.lower()):
                city_match = city
                print(f"🔍 Phát hiện thành phố trong truy vấn: {city}")
                break
                
        # Perform the search
        try:
            print(f"ℹ️ Performing similarity search in FAISS index...")
            
            # Nếu có thành phố trong query, ưu tiên kết quả từ file tương ứng
            if city_match:
                # Tìm kiếm thông thường
                all_docs = self.vector_store.similarity_search(query, k=k+6)  # Lấy thêm kết quả để lọc
                
                # Lọc kết quả theo thành phố
                priority_docs = []
                other_docs = []
                
                city_file_patterns = {
                    "hcm": r'vietnam_hochiminh\.txt$',
                    "hanoi": r'vietnam_hanoi\.txt$',
                    "hue": r'vietnam_hue\.txt$',
                    "danang": r'vietnam_danang\.txt$',
                    "vungtau": r'vietnam_vungtau\.txt$'
                }
                
                pattern = city_file_patterns[city_match]
                print(f"🔍 Ưu tiên tìm kiếm từ file khớp với mẫu: {pattern}")
                
                for doc in all_docs:
                    source = doc.metadata.get("source", "")
                    if re.search(pattern, source, re.IGNORECASE):
                        priority_docs.append(doc)
                        print(f"✅ Tìm thấy tài liệu ưu tiên từ nguồn: {source}")
                    else:
                        other_docs.append(doc)
                
                # Kết hợp kết quả, ưu tiên file thành phố
                docs = priority_docs + other_docs
                docs = docs[:k]  # Giới hạn số lượng kết quả
                print(f"✅ Đã ưu tiên {len(priority_docs)} tài liệu phù hợp với thành phố {city_match}")
            else:
                # Tìm kiếm thông thường nếu không có thành phố trong query
                docs = self.vector_store.similarity_search(query, k=k)
                
            print(f"✅ Found {len(docs)} relevant document chunks.")
            print("--- Search Finished ---")
            return docs
        except Exception as e:
            print(f"❌ Error during similarity search: {e}")
            print("--- Search Failed ---")
            return []