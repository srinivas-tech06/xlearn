"""
RAG Engine — Retrieval-Augmented Generation with FAISS vector store.
Provides semantic knowledge retrieval for context-aware AI responses.
Falls back gracefully if sentence-transformers or faiss are not available.
"""
import json
import re
from typing import List, Optional

# Graceful imports
try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("[RAG Engine] faiss/sentence-transformers not available — using keyword fallback")


# ─────────────────────────────────────────────────────────────
# Built-in Knowledge Base (no files needed)
# ─────────────────────────────────────────────────────────────
KNOWLEDGE_BASE = [
    # Python
    {"id": "py_vars", "topic": "variables", "subject": "python", "content": "Variables in Python are dynamically typed containers. Use = for assignment. Python has int, float, str, bool, list, dict, tuple, set types. Variables don't need declaration — just assign. Example: x = 10, name = 'Alice', is_active = True"},
    {"id": "py_loops", "topic": "loops", "subject": "python", "content": "Python has two loop types: for loops iterate over sequences (for x in range(10)), while loops repeat while condition is True. Use break to exit, continue to skip. List comprehensions [x*2 for x in range(5)] are concise loop alternatives."},
    {"id": "py_functions", "topic": "functions", "subject": "python", "content": "Define functions with def keyword. Parameters can have defaults. *args collects positional args as tuple, **kwargs collects keyword args as dict. Lambda creates anonymous functions. Functions are first-class objects in Python."},
    {"id": "py_oop", "topic": "object oriented programming", "subject": "python", "content": "Classes use class keyword. __init__ is the constructor, self refers to instance. Inheritance: class Child(Parent). super() calls parent methods. @property for getters/setters. Encapsulation uses _ prefix for private."},
    {"id": "py_lists", "topic": "lists", "subject": "python", "content": "Lists are ordered, mutable sequences. Create with [], use append(), extend(), insert(), remove(), pop(). Slice with [start:end:step]. Sort with sort() or sorted(). List comprehensions for concise creation."},
    {"id": "py_dicts", "topic": "dictionaries", "subject": "python", "content": "Dicts store key-value pairs. Access with dict[key] or dict.get(key, default). Iterate with .items(), .keys(), .values(). Dict comprehensions work too. keys must be hashable. Nested dicts are common for complex data."},
    {"id": "py_exceptions", "topic": "exceptions", "subject": "python", "content": "Use try/except/finally for error handling. Catch specific exceptions: except ValueError, except TypeError. Raise custom exceptions with class MyError(Exception). The finally block always runs. Use with statement for context managers."},
    # Machine Learning
    {"id": "ml_supervised", "topic": "supervised learning", "subject": "machine learning", "content": "Supervised learning trains on labeled data (input-output pairs). Key algorithms: Linear Regression (continuous output), Logistic Regression (binary classification), Decision Trees, Random Forest, SVM. Evaluate with train/test split and cross-validation."},
    {"id": "ml_neural", "topic": "neural networks", "subject": "machine learning", "content": "Neural networks have input layer, hidden layers, output layer. Neurons apply activation functions (ReLU, sigmoid, softmax). Backpropagation computes gradients. Adam optimizer is most popular. Batch normalization helps training stability."},
    {"id": "ml_overfitting", "topic": "overfitting", "subject": "machine learning", "content": "Overfitting: model memorizes training data, fails on new data. Solutions: more data, dropout, regularization (L1/L2), early stopping, cross-validation. Underfitting: model too simple — increase complexity or features."},
    # Web Development
    {"id": "web_html", "topic": "html", "subject": "web development", "content": "HTML structures web pages with semantic tags: <header>, <main>, <article>, <section>, <footer>. Use <div> for layout containers. Forms use <form>, <input>, <button>. Always include alt text for images. HTML5 added canvas, video, audio elements."},
    {"id": "web_css", "topic": "css", "subject": "web development", "content": "CSS styles HTML with selectors and properties. Box model: content + padding + border + margin. Flexbox for 1D layout, Grid for 2D. Media queries for responsive design. CSS variables (--color: #fff) for reuse. Transitions and animations for interactivity."},
    {"id": "web_react", "topic": "react", "subject": "web development", "content": "React builds UIs with components. useState for local state, useEffect for side effects, useContext for shared state. JSX renders HTML-like syntax. Props pass data down, callbacks pass events up. Virtual DOM diffing makes updates efficient."},
    # SQL
    {"id": "sql_basics", "topic": "sql basics", "subject": "databases", "content": "SQL: SELECT columns FROM table WHERE condition. JOIN combines tables: INNER JOIN (matching rows), LEFT JOIN (all left + matching right). GROUP BY aggregates with COUNT(), SUM(), AVG(). ORDER BY sorts results. LIMIT/OFFSET for pagination."},
    {"id": "sql_indexes", "topic": "database indexes", "subject": "databases", "content": "Indexes speed up queries by creating lookup structures. B-tree indexes for range queries, hash indexes for equality. Too many indexes slow writes. Primary key is auto-indexed. Composite indexes for multi-column lookups. Explain plans show how queries use indexes."},
    # Algorithms
    {"id": "algo_bigO", "topic": "big o notation", "subject": "algorithms", "content": "Big O measures algorithm efficiency. O(1) constant, O(log n) logarithmic, O(n) linear, O(n log n) linearithmic, O(n²) quadratic, O(2^n) exponential. Always analyze worst case. Space complexity measures memory usage similarly."},
    {"id": "algo_sorting", "topic": "sorting algorithms", "subject": "algorithms", "content": "Common sorts: Bubble O(n²), Selection O(n²), Insertion O(n²) - simple but slow. Merge Sort O(n log n) - stable, divide and conquer. Quick Sort O(n log n) avg - in-place. Python's sort uses Timsort O(n log n)."},
    # Cloud
    {"id": "cloud_aws", "topic": "cloud computing", "subject": "devops", "content": "Cloud services: IaaS (virtual machines, storage), PaaS (managed databases, runtimes), SaaS (complete apps). AWS key services: EC2 (compute), S3 (storage), RDS (database), Lambda (serverless). Understand VPCs, security groups, IAM roles."},
]


class RAGEngine:
    def __init__(self):
        self.available = RAG_AVAILABLE
        self.index = None
        self.documents = KNOWLEDGE_BASE
        self.model = None

        if self.available:
            self._build_index()

    def _build_index(self):
        """Build FAISS vector index from knowledge base."""
        try:
            print("[RAG Engine] Loading sentence transformer model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            texts = [f"{doc['topic']}: {doc['content']}" for doc in self.documents]
            embeddings = self.model.encode(texts, show_progress_bar=False)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)
            faiss.normalize_L2(embeddings)
            self.index.add(embeddings.astype(np.float32))
            print(f"[RAG Engine] ✅ Vector index built with {len(self.documents)} documents")
        except Exception as e:
            print(f"[RAG Engine] Index build failed: {e} — using keyword fallback")
            self.available = False

    def retrieve(self, query: str, k: int = 3) -> List[dict]:
        """Retrieve top-k most relevant documents for a query."""
        if self.available and self.index is not None:
            return self._vector_retrieve(query, k)
        return self._keyword_retrieve(query, k)

    def _vector_retrieve(self, query: str, k: int) -> List[dict]:
        """Semantic vector search via FAISS."""
        try:
            query_vec = self.model.encode([query], show_progress_bar=False)
            faiss.normalize_L2(query_vec)
            scores, indices = self.index.search(query_vec.astype(np.float32), k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and score > 0.2:
                    doc = self.documents[idx].copy()
                    doc["relevance_score"] = float(score)
                    results.append(doc)
            return results
        except Exception as e:
            print(f"[RAG Engine] Vector search failed: {e}")
            return self._keyword_retrieve(query, k)

    def _keyword_retrieve(self, query: str, k: int) -> List[dict]:
        """Fallback keyword-based retrieval."""
        query_lower = query.lower()
        scored = []
        for doc in self.documents:
            score = 0
            topic_words = doc["topic"].lower().split()
            for word in topic_words:
                if word in query_lower:
                    score += 2
            if doc["subject"].lower() in query_lower:
                score += 1
            # Match content words
            content_words = set(doc["content"].lower().split())
            query_words = set(query_lower.split())
            overlap = content_words & query_words
            score += len(overlap) * 0.1
            if score > 0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scored[:k]:
            d = doc.copy()
            d["relevance_score"] = score
            results.append(d)
        return results

    def format_context(self, docs: List[dict]) -> str:
        """Format retrieved documents into a context string for LLM."""
        if not docs:
            return ""
        parts = ["📚 **Relevant Knowledge:**"]
        for doc in docs:
            parts.append(f"\n**{doc['topic'].title()}** ({doc['subject']}):\n{doc['content']}")
        return "\n".join(parts)

    def add_document(self, topic: str, subject: str, content: str):
        """Dynamically add a document to the knowledge base."""
        doc = {
            "id": f"custom_{len(self.documents)}",
            "topic": topic,
            "subject": subject,
            "content": content
        }
        self.documents.append(doc)
        if self.available and self.model and self.index:
            try:
                text = f"{topic}: {content}"
                vec = self.model.encode([text], show_progress_bar=False)
                faiss.normalize_L2(vec)
                self.index.add(vec.astype(np.float32))
            except Exception:
                pass


# Singleton
rag_engine = RAGEngine()
