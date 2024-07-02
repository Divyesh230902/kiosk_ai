import os
import re
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

DATA_PATH = "knowlegde_base"
DB_PATH = "chroma_db"
# QA_CHAIN_PROMPT = hub.pull("rlm/rag-prompt-mistral")
QA_CHAIN_PROMPT = PromptTemplate.from_template(
    "<s> [INST] You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise. [/INST] </s> \n[INST] Question: {question} \nContext: {context} \nAnswer: [/INST]")

class UniversityChatbot:
    def __init__(self):
        try:
            self.llm = Ollama(model="mistral", verbose=True, callback_manager=CallbackManager(
                [StreamingStdOutCallbackHandler()]),)
            self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
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
            vectorstore = Chroma(persist_directory=DB_PATH,
                                 embedding_function=self.embedding_function)
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
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1500, chunk_overlap=150)
            texts = text_splitter.split_documents(documents)
            vectorstore = Chroma.from_documents(texts, self.embedding_function, persist_directory=DB_PATH)
            # vectorstore.persist()
        except Exception as e:
            print(f"Error creating vector database: {e}")

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

            # Handling remaining specific case
            if normalized_prompt == "hi":
                normalized_prompt = "hello"
            elif normalized_prompt == "ok":
                return "Is there anything else I can help you with?", None

            chain = self.qa_bot()
            response = chain.invoke(prompt)
            answer = response["result"]
            answer = answer.replace(".", ".\n")
            return answer, response["source_documents"]
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
