# rhetorical_elements_agent.py
from enum import Enum

from sentence_transformers import SentenceTransformer

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
 
from backend.app.agents.base_agent import BaseAgent
from backend.app.config.config import Config
from backend.app.utils.debate import *

class EmbeddingModelType(Enum):
    OPENAI = "openai"
    LABSE = "labse"

class RhetoricalElementsAgent(BaseAgent):
    def __init__(self,
                llm_model,
                embedding_model:EmbeddingModelType = "openai"):

        self.llm_model = llm_model
        try:
            model_type_enum = EmbeddingModelType(embedding_model)
        except ValueError:
            raise ValueError(f"Invalid model_type '{embedding_model}'. Allowed values are: 'openai', 'labse'")
    
        if model_type_enum == EmbeddingModelType.OPENAI:
            print("Using OpenAI embedding model", flush = True)
            self.embedding_model = OpenAIEmbeddings(api_key= Config.OPENAI_API_KEY, model="text-embedding-3-large")
        elif model_type_enum == EmbeddingModelType.LABSE:
            print("Using LaBSE model", flush = True)
            # Check if the model exists locally
            if Config.LABSE_MODEL_PATH.exists():
                print(f"Loading model from local path: {Config.LABSE_MODEL_PATH}", flush = True)
                self.embedding_model = HuggingFaceEmbeddings(model_name = str(Config.LABSE_MODEL_PATH))
            else:
                print(f"Local path not found. Downloading model: {LABSE_MODEL_NAME}", flush = True)
                self.embedding_model = SentenceTransformer(LABSE_MODEL_NAME)
                self.embedding_model.save(str(Config.LABSE_MODEL_PATH))
                self.embedding_model = HuggingFaceEmbeddings(model_name = str(Config.LABSE_MODEL_PATH))

        self._load_knowledge_base()
        self._prepare_docs()
        self._create_retriever()
        self._prepare_rag_prompt()
        self._prepare_rag_chain()

    def _load_knowledge_base(self):
        with open(Config.BALAGA_KNOWLEDGE_BASE_PATH) as f:
            self.knowledge_base = f.read()

    def _prepare_docs(self):
        self._load_knowledge_base()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=100)
        self.splits = text_splitter.create_documents([self.knowledge_base])

    def _create_retriever(self):
        vectorstore = FAISS.from_documents(self.splits, self.embedding_model)
        self.retriever = vectorstore.as_retriever() 

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def _prepare_rag_prompt(self):
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("user", "{الشرح}"),
            ("system", " انت خبير في علم البلاغة في اللغة العربية و معك شرح مختلف ﻷقسام البلاغة و الانواع المختلفة سوف أرفق لك بيت شعري و أنت تستخرج فقط خمس من مواطن البلاغة والجمال المختلفة"),
            ("user", "{البيت}"),
        ])

    def _prepare_rag_chain(self):
        self.rag_chain = (
            {"الشرح": self.retriever | self._format_docs,"البيت": RunnablePassthrough()}
            | self.rag_prompt
            | self.llm_model.get_langchain_model()
            | StrOutputParser()
        )

    def extract_rhetorical_elements(self, bait):
        rhetorical_analysis = self.rag_chain.invoke(bait)
        return rhetorical_analysis