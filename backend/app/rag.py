from typing import List, Tuple
import os

import chromadb
from sentence_transformers import SentenceTransformer
from openai import OpenAI

from app.config import VECTOR_DB_DIR, COLLECTION_NAME, EMBEDDING_MODEL_NAME


class RAGPipeline:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        self.collection = self.client.get_collection(COLLECTION_NAME)
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

        # ✅ get key from env (NOT hard-coded)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm_client = None
        if self.openai_api_key:
            print("OpenAI key loaded, LLM client enabled")  # temporary debug
            self.llm_client = OpenAI(api_key=self.openai_api_key)
        else:
            print("No OpenAI key found, using demo answers")  # temporary debug

    def retrieve(self, question: str, top_k: int = 4):
        result = self.collection.query(
            query_texts=[question],
            n_results=top_k,
        )
        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        return documents, metadatas

    def build_prompt(self, question: str, documents: List[str]) -> str:
        context = "\n\n---\n\n".join(documents) if documents else "No relevant context."
        return (
            "You are a helpful assistant. Answer the question based ONLY on the context.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\n\n"
            "If the answer is not in the context, say you don't know.\n"
            "Answer concisely."
        )

    def _generate_with_openai(self, prompt: str) -> str:
        if self.llm_client is None:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
        )
        return response.choices[0].message.content

    def generate_answer(self, question: str, documents: List[str]) -> str:
        prompt = self.build_prompt(question, documents)

        # ✅ try to use real LLM first
        if self.llm_client is not None:
            try:
                return self._generate_with_openai(prompt)
            except Exception as e:
                return (
                    "LLM generation failed, falling back to demo answer.\n\n"
                    f"(Error: {e})\n\n"
                    f"Prompt preview:\n{prompt[:500]}..."
                )

        # 🔁 fallback demo mode
        return f"(Demo answer based on retrieved context)\n\n{prompt[:500]}..."

    def answer_question(self, question: str):
        documents, metadatas = self.retrieve(question)
        answer = self.generate_answer(question, documents)
        sources = sorted({m["source"] for m in metadatas})
        return answer, list(sources)


rag_pipeline = RAGPipeline()
