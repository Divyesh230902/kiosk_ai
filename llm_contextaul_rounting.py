import os
import re
import numpy as np
from langchain_community.llms import Ollama
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain import hub
from conversational import get_specific_prompt_response, handle_greetings, handle_gratitude, handle_farewells

# Path definitions
DATA_PATH = "knowledge_base"
DB_PATH = "chroma_db"
QA_CHAIN_PROMPT = hub.pull("rlm/rag-prompt-mistral")

# Predefined context templates
ADMISSIONS_TEMPLATE = "You are an expert on admissions at Silver Oak University. Answer the following question: {query}"
COURSES_TEMPLATE = "You are knowledgeable about the courses offered at Silver Oak University. Answer the following question: {query}"
LABS_TEMPLATE = "You are familiar with the labs and facilities at Silver Oak University. Answer the following question: {query}"

# Cosine similarity function
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    dot_product = np.dot(a, b.T)
    norm_a = np.linalg.norm(a, axis=1, keepdims=True)
    norm_b = np.linalg.norm(b, axis=1, keepdims=True)
    return dot_product / (norm_a * norm_b.T)

class UniversityChatbot:
    def __init__(self):
        try:
            self.llm = Ollama(model="mistral", verbose=True, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
            self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            self.context_templates = [ADMISSIONS_TEMPLATE, COURSES_TEMPLATE, LABS_TEMPLATE]
            self.context_embeddings = self.embedding_function.embed_documents(self.context_templates)
            if not os.path.exists(DB_PATH):
                self.create_vector_db()
        except Exception as e:
            print(f"Error initializing knowledge base: {e}")

    def retrieval_qa_chain(self, llm, vectorstore):
        try:
            qa_chain = RetrievalQA.from_chain_type(
                llm,
                retriever=vectorstore.as_retriever(),
                chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
                return_source_documents=True,
            )
            return qa_chain
        except Exception as e:
            print(f"Error creating retrieval QA chain: {e}")
            return None

    def qa_bot(self):
        try:
            llm = self.llm
            vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=self.embedding_function)
            qa = self.retrieval_qa_chain(llm, vectorstore)
            return qa
        except Exception as e:
            print(f"Error initializing QA bot: {e}")
            return None

    def create_vector_db(self):
        try:
            loader = PyPDFDirectoryLoader(DATA_PATH)
            documents = loader.load()
            print(f"Processed {len(documents)} pdf files")
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
            texts = text_splitter.split_documents(documents)
            vectorstore = Chroma.from_documents(texts, self.embedding_function, persist_directory=DB_PATH)
            vectorstore.persist()
        except Exception as e:
            print(f"Error creating vector database: {e}")

    def prompt_router(self, query):
        try:
            query_embedding = self.embedding_function.embed_query(query)
            similarity_scores = cosine_similarity([query_embedding], self.context_embeddings)[0]
            most_similar_index = similarity_scores.argmax()
            selected_template = self.context_templates[most_similar_index]
            return PromptTemplate.from_template(selected_template)
        except Exception as e:
            print(f"Error routing prompt: {e}")
            return PromptTemplate.from_template(ADMISSIONS_TEMPLATE)

    def clean_response(self, response):
        # Remove unwanted characters or formatting
        cleaned_response = re.sub(r'\s+', ' ', response).strip()
        return cleaned_response

    def _answer(self, prompt):
        try:
            # Normalize the prompt
            normalized_prompt = re.sub(r'\W+', ' ', prompt.lower().strip())

            # Check for specific prompts using the imported function
            specific_response = get_specific_prompt_response(normalized_prompt)
            if specific_response:
                return specific_response, None

            # Check for greetings
            greeting_response = handle_greetings(normalized_prompt)
            if greeting_response:
                return greeting_response, None

            # Check for expressions of gratitude
            gratitude_response = handle_gratitude(normalized_prompt)
            if gratitude_response:
                return gratitude_response, None

            # Check for farewells
            farewell_response = handle_farewells(normalized_prompt)
            if farewell_response:
                return farewell_response, None

            # Route to the appropriate context
            selected_prompt_template = self.prompt_router(prompt)
            chain = self.qa_bot()
            response = chain.invoke(selected_prompt_template.format(query=prompt))
            answer = response["result"]
            cleaned_answer = self.clean_response(answer)
            return cleaned_answer, response["source_documents"]
        except Exception as e:
            print(f"Error answering prompt: {e}")
            return "I'm sorry, I encountered an error while processing your request.", None

    def chat(self, prompt):
        try:
            response, _ = self._answer(prompt)
            return response
        except Exception as e:
            print(f"Error during chat: {e}")
            return "I'm sorry, I encountered an error while processing your request."

    def chat_stream(self, prompt):
        try:
            response, docs = self._answer(prompt)
            for r in response:
                yield r, docs
        except Exception as e:
            print(f"Error during chat stream: {e}")
            yield "I'm sorry, I encountered an error while processing your request.", None

# Usage example
# if __name__ == "__main__":
#     chatbot = UniversityChatbot()
#     prompt = "Tell me about the labs at Silver Oak University."
#     response = chatbot.chat(prompt)
#     print(response)
