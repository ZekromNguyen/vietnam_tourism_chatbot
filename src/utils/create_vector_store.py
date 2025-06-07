from src.core.retriever import DocumentRetriever
from dotenv import load_dotenv
import os
import sys

def main():
    # Load environment variables
    load_dotenv()

    # Check if GOOGLE API key is set
    if not os.getenv("GOOGLE_API_KEY"):
        print("🔴 Error: Please set your GOOGLE_API_KEY in the .env file")
        print("Get one from Google AI Studio: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    print("Attempting to create vector store using Google Embeddings...")
    try:
        # Initialize retriever (uses Google Embeddings by default now)
        retriever = DocumentRetriever()
        vector_store = retriever.create_vector_store()

        if vector_store:
            print("\n✅ Vector store created successfully!")
            # Optionally check the number of vectors/documents indexed
            # Note: retriever.load_documents() might reload, accessing vector_store directly might be better if possible
            # Example: Check FAISS index size if accessible
            if hasattr(vector_store, 'index'):
                 print(f"Number of vectors indexed in FAISS: {vector_store.index.ntotal}")
            print("Your Vietnam tourism chatbot knowledge base is ready.")
            return 0
        else:
            print("\n❌ Failed to create vector store. Please check logs and ensure documents exist in the 'data' directory.")
            return 1

    except ValueError as e:
         print(f"🔴 Configuration Error: {e}")
         return 1
    except Exception as e:
         print(f"🔴 An unexpected error occurred: {e}")
         # Log traceback for detailed debugging
         import traceback
         print(traceback.format_exc())
         return 1

if __name__ == "__main__":
    sys.exit(main())