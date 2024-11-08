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
    """
    Enum to specify the type of embedding model used: OpenAI or LaBSE.
    """
    OPENAI = "openai"
    LABSE = "labse"

class RhetoricalElementsAgent(BaseAgent):
    """
    Agent for extracting rhetorical elements and beauty from Arabic poetry using language models and embeddings.

    Uses retrieval-augmented generation (RAG) to analyze poetry and provide insights into its rhetorical elements.
    """

    def __init__(self, llm_model, embedding_model: EmbeddingModelType = "openai"):
        """
        Initializes the RhetoricalElementsAgent with the specified LLM model and embedding model.

        :param llm_model: The language model used for generating or analyzing the text.
        :param embedding_model: The embedding model to use for transforming texts (either 'openai' or 'labse').
        :raises ValueError: If an invalid embedding model is specified.
        """
        self.llm_model = llm_model
        try:
            model_type_enum = EmbeddingModelType(embedding_model)
        except ValueError:
            raise ValueError(f"Invalid model_type '{embedding_model}'. Allowed values are: 'openai', 'labse'")

        # Load the appropriate embedding model based on the specified type
        if model_type_enum == EmbeddingModelType.OPENAI:
            print("Using OpenAI embedding model", flush=True)
            self.embedding_model = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY, model="text-embedding-3-large")
        elif model_type_enum == EmbeddingModelType.LABSE:
            print("Using LaBSE model", flush=True)
            # Check if the LaBSE model exists locally, otherwise download and save it
            if Config.LABSE_MODEL_PATH.exists():
                print(f"Loading model from local path: {Config.LABSE_MODEL_PATH}", flush=True)
                self.embedding_model = HuggingFaceEmbeddings(model_name=str(Config.LABSE_MODEL_PATH))
            else:
                print(f"Local path not found. Downloading model: {LABSE_MODEL_NAME}", flush=True)
                self.embedding_model = SentenceTransformer(LABSE_MODEL_NAME)
                self.embedding_model.save(str(Config.LABSE_MODEL_PATH))
                self.embedding_model = HuggingFaceEmbeddings(model_name=str(Config.LABSE_MODEL_PATH))

        # Load the knowledge base and prepare documents for retrieval
        self._load_knowledge_base()
        self._prepare_docs()
        self._create_retriever()

        # Prepare the RAG prompt and chain for extraction
        self._prepare_rag_prompt()
        self._prepare_rag_chain()

    def _load_knowledge_base(self):
        """
        Loads the knowledge base from a file that contains a collection of rhetorical explanations.

        The knowledge base is stored in the `BALAGA_KNOWLEDGE_BASE_PATH` configuration path.
        """
        with open(Config.BALAGA_KNOWLEDGE_BASE_PATH) as f:
            self.knowledge_base = f.read()

    def _prepare_docs(self):
        """
        Prepares the knowledge base documents by splitting them into smaller chunks for efficient retrieval.

        Uses a text splitter that divides the knowledge base into chunks of up to 4000 characters, with 100-character overlap.
        """
        self._load_knowledge_base()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=100)
        self.splits = text_splitter.create_documents([self.knowledge_base])

    def _create_retriever(self):
        """
        Creates a retriever using FAISS vectorstore for efficient similarity search.

        The retriever is created from the documents split earlier, using the selected embedding model.
        """
        vectorstore = FAISS.from_documents(self.splits, self.embedding_model)
        self.retriever = vectorstore.as_retriever()

    def _format_docs(self, docs):
        """
        Formats the retrieved documents into a human-readable format by concatenating the page contents.

        :param docs: The list of documents to format
        :return: A string containing the formatted documents
        """
        return "\n\n".join(doc.page_content for doc in docs)

    def _prepare_rag_prompt(self):
        """
        Prepares the RAG (retrieval-augmented generation) prompt template for generating explanations.

        The prompt template includes instructions in Arabic for analyzing rhetorical elements in a given verse.
        """
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("user", "{الشرح}"),
            ("system", " انت خبير في علم البلاغة في اللغة العربية و معك شرح مختلف ﻷقسام البلاغة و الانواع المختلفة سوف أرفق لك بيت شعري و أنت تستخرج فقط خمس من مواطن البلاغة والجمال المختلفة"),
            ("user", "{البيت}"),
        ])

    def _prepare_rag_chain(self):
        """
        Prepares the RAG chain, which combines retrieval, prompt, and language model for analysis.

        The chain retrieves relevant documents, formats them, passes them to the prompt, and then generates the final output.
        """
        self.rag_chain = (
            {"الشرح": self.retriever | self._format_docs, "البيت": RunnablePassthrough()}
            | self.rag_prompt
            | self.llm_model.get_langchain_model()
            | StrOutputParser()
        )

    def extract_rhetorical_elements(self, bait):
        """
        Extracts the rhetorical elements from a given Arabic poetic verse.

        :param bait: The Arabic verse (bait) to analyze
        :return: The rhetorical analysis generated by the RAG chain
        """
        rhetorical_analysis = self.rag_chain.invoke(bait)
        return rhetorical_analysis
