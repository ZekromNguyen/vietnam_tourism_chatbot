# Import necessary Gemini components
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain # Keep this for Gemini as well
# Import prompt templates
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
import os
import warnings

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
**Quan trọng: Hãy luôn trả lời bằng tiếng Việt.**

Respond helpfully based on the provided context, your persona, and the chat history.
"""
# --- End of Persona System Prompt ---

class ResponseGenerator:
    def __init__(self, retriever, model_name="gemini-1.5-flash"):
        self.retriever = retriever
        self.model_name = model_name

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

    def generate_response(self, query):
        """Generate a response for the user query using Gemini and the defined persona"""
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