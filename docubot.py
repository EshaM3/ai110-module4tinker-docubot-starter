"""
Core DocuBot class responsible for:
- Loading documents from the docs/ folder
- Building a simple retrieval index (Phase 1)
- Retrieving relevant snippets (Phase 1)
- Supporting retrieval only answers
- Supporting RAG answers when paired with Gemini (Phase 2)
"""

import os
import glob

class DocuBot:
    def __init__(self, docs_folder="docs", llm_client=None):
        """
        docs_folder: directory containing project documentation files
        llm_client: optional Gemini client for LLM based answers
        """
        self.docs_folder = docs_folder
        self.llm_client = llm_client

        # Load documents into memory
        self.documents = self.load_documents()  # List of (filename, text)

        # Build a retrieval index (implemented in Phase 1)
        self.index = self.build_index(self.documents)

    # -----------------------------------------------------------
    # Document Loading
    # -----------------------------------------------------------

    def load_documents(self):
        """
        Loads all .md and .txt files inside docs_folder.
        Returns a list of tuples: (filename, text)
        """
        docs = []
        pattern = os.path.join(self.docs_folder, "*.*")
        for path in glob.glob(pattern):
            if path.endswith(".md") or path.endswith(".txt"):
                with open(path, "r", encoding="utf8") as f:
                    text = f.read()
                filename = os.path.basename(path)
                docs.append((filename, text))
        return docs

    # -----------------------------------------------------------
    # Token Normalization
    # -----------------------------------------------------------

    def _normalize(self, word):
        """
        Lowercase, strip punctuation, and apply simple stemming.
        Strips a trailing 's' from words longer than 3 characters
        so that e.g. 'endpoints' matches 'endpoint'.
        """
        word = word.strip(",.!?:;\"'()[]").lower()
        if len(word) > 3 and word.endswith("s"):
            word = word[:-1]
        return word

    # -----------------------------------------------------------
    # Index Construction (Phase 1)
    # -----------------------------------------------------------

    def build_index(self, documents):
        """
        TODO (Phase 1):
        Build a tiny inverted index mapping lowercase words to the documents
        they appear in.

        Example structure:
        {
            "token": ["AUTH.md", "API_REFERENCE.md"],
            "database": ["DATABASE.md"]
        }

        Keep this simple: split on whitespace, lowercase tokens,
        ignore punctuation if needed.
        """
        index = {}
        for filename, text in documents:
            for word in text.split():
                word = self._normalize(word)
                if not word:
                    continue
                index.setdefault(word, [])
                if filename not in index[word]:
                    index[word].append(filename)
        return index

    # -----------------------------------------------------------
    # Scoring and Retrieval (Phase 1)
    # -----------------------------------------------------------

    def score_document(self, query, text):
        """
        TODO (Phase 1):
        Return a simple relevance score for how well the text matches the query.

        Suggested baseline:
        - Convert query into lowercase words
        - Count how many appear in the text
        - Return the count as the score
        """
        counter = 0
        text_words = set(self._normalize(w) for w in text.split())
        for word in query.split():
            word = self._normalize(word)
            if word in text_words:
                counter += 1
        return counter

    def retrieve(self, query, top_k=3, min_score=2):
        """
        Use the index and scoring function to select top_k relevant document snippets.

        Returns a list of (filename, text) sorted by score descending.
        Sections scoring below min_score are excluded as insufficient evidence.
        """
        # Find candidate filenames from the index
        candidates = set()
        for word in query.split():
            word = self._normalize(word)
            if word in self.index:
                candidates.update(self.index[word])

        # Score each section of each candidate document
        doc_lookup = dict(self.documents)
        scored = []
        for filename in candidates:
            sections = doc_lookup[filename].split("\n\n")
            for i, section in enumerate(sections):
                section = section.strip()
                if not section:
                    continue
                score = self.score_document(query, section)
                if score >= min_score:
                    prev_section = sections.copy()[i - 1].strip() if i > 0 else ""
                    display = (prev_section + "\n\n" + section).strip() if prev_section else section
                    scored.append((filename, display, score))

        # Sort by score descending and return top_k as (filename, text)
        scored.sort(key=lambda x: x[2], reverse=True)
        return [(filename, text) for filename, text, _ in scored][:top_k]

    # -----------------------------------------------------------
    # Answering Modes
    # -----------------------------------------------------------

    def answer_retrieval_only(self, query, top_k=3):
        """
        Phase 1 retrieval only mode.
        Returns raw snippets and filenames with no LLM involved.
        """
        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        formatted = []
        for filename, text in snippets:
            formatted.append(f"[{filename}]\n{text}\n")

        return "\n---\n".join(formatted)

    def answer_rag(self, query, top_k=3):
        """
        Phase 2 RAG mode.
        Uses student retrieval to select snippets, then asks Gemini
        to generate an answer using only those snippets.
        """
        if self.llm_client is None:
            raise RuntimeError(
                "RAG mode requires an LLM client. Provide a GeminiClient instance."
            )

        snippets = self.retrieve(query, top_k=top_k)

        if not snippets:
            return "I do not know based on these docs."

        return self.llm_client.answer_from_snippets(query, snippets)

    # -----------------------------------------------------------
    # Bonus Helper: concatenated docs for naive generation mode
    # -----------------------------------------------------------

    def full_corpus_text(self):
        """
        Returns all documents concatenated into a single string.
        This is used in Phase 0 for naive 'generation only' baselines.
        """
        return "\n\n".join(text for _, text in self.documents)
