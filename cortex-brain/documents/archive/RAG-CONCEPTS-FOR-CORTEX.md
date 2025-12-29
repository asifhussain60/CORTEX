# RAG Concepts Filtered for CORTEX 4.0

**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** December 18, 2025  
**Purpose:** Simplified RAG concepts applicable to CORTEX 4.0 guideline content stores

---

## 🎯 What is RAG? (Simplified for CORTEX)

**RAG = Retrieval-Augmented Generation**

Think of it like this:
1. **Retrieval** - Find relevant documents/chunks from your knowledge base
2. **Augmentation** - Add those documents to the LLM's prompt context
3. **Generation** - LLM generates a response using both its training AND your documents

**Why RAG for CORTEX?**
- Users ask: "What's our HSA PHI redaction standard?"
- CORTEX has NO domain-specific guidelines (only learned patterns)
- RAG lets teams upload guidelines that CORTEX references before responding

---

## 📚 Core RAG Components (What CORTEX Needs)

### 1. Document Chunking

**Problem:** LLMs have context limits (can't read entire 50-page document).

**Solution:** Break documents into small, overlapping chunks.

```
Full Document (50 pages)
    ↓
Chunk 1: "HSA PHI Redaction: Always use AES-256..." (400 chars)
Chunk 2: "...AES-256 encryption for data at rest. Use bcrypt..." (400 chars) ← 50-char overlap
Chunk 3: "...bcrypt (cost=12) for passwords. Redact SSN..." (400 chars)
```

**Best Practices:**
- **Chunk size:** 200-500 characters (balances context vs precision)
- **Overlap:** 50-100 characters (preserves context across boundaries)
- **Split at:** Sentence boundaries (not mid-sentence)

**Tool:** LangChain `RecursiveCharacterTextSplitter`

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " "]
)

chunks = splitter.split_text(guideline_document)
```

---

### 2. Embeddings (Semantic Vectors)

**Problem:** Keyword search fails if user says "allowance" but doc says "reimbursement".

**Solution:** Convert text to numbers (vectors) that capture meaning.

```
Text: "HSA PHI redaction standard"
    ↓ (embedding model)
Vector: [0.23, -0.45, 0.67, ..., 0.12]  # 384 numbers
```

**How it works:**
- Similar meanings → Similar vectors
- "PHI redaction" and "privacy protection" → Close vectors
- "PHI redaction" and "payment processing" → Far apart vectors

**Model for CORTEX:** `sentence-transformers/all-MiniLM-L6-v2`

**Why this model?**
- ✅ Small (90MB) - Runs locally on CPU
- ✅ Fast (22M parameters)
- ✅ Proven (top 10 on Hugging Face)
- ✅ 384 dimensions (good precision)
- ❌ Not state-of-the-art (but sufficient)

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embedding
text = "HSA PHI redaction standard"
embedding = model.encode(text)  # Returns 384-dim vector
```

---

### 3. Vector Storage

**Problem:** Need to store thousands of embeddings and search them fast.

**Solution:** Store embeddings in a database with efficient search.

**CORTEX Approach:** SQLite with BLOB column (simple, proven)

```sql
CREATE TABLE guideline_chunks (
    id INTEGER PRIMARY KEY,
    content TEXT,
    embedding BLOB,  -- Store 384-dim vector as binary
    document_title TEXT,
    namespace TEXT
);
```

**Why SQLite (not vector DB like Pinecone)?**
- ✅ Already used in CORTEX brain (consistent tech stack)
- ✅ Handles 10,000+ chunks easily
- ✅ No external dependencies (runs locally)
- ✅ Zero cloud costs
- ⚠️ For 50,000+ chunks, consider FAISS (local vector index)

---

### 4. Semantic Search

**Problem:** Find the 3 most relevant chunks for user's question.

**Solution:** Compare query vector to all chunk vectors, return top matches.

```python
import numpy as np

def search_guidelines(query: str, chunks: list) -> list:
    # 1. Generate query embedding
    query_vector = model.encode(query)
    
    # 2. Calculate similarity to each chunk
    results = []
    for chunk in chunks:
        chunk_vector = np.frombuffer(chunk['embedding'])
        
        # Cosine similarity (dot product of normalized vectors)
        similarity = np.dot(query_vector, chunk_vector)
        
        results.append({
            "content": chunk['content'],
            "similarity": float(similarity),
            "title": chunk['document_title']
        })
    
    # 3. Sort by similarity, return top 3
    results.sort(key=lambda x: x['similarity'], reverse=True)
    return results[:3]
```

**Similarity Score Interpretation:**
- 0.9 - 1.0: Extremely relevant (same topic)
- 0.7 - 0.9: Highly relevant (related topic)
- 0.5 - 0.7: Moderately relevant (tangentially related)
- < 0.5: Not relevant (ignore)

---

### 5. RAG Pipeline (Putting It Together)

**Full Workflow:**

```
User Query: "What's our HSA PHI redaction standard?"
    ↓
1. RETRIEVAL
   - Generate query embedding
   - Search guidelines.db
   - Return top 3 chunks (similarity > 0.7)
   
2. AUGMENTATION
   - Build LLM prompt:
     "Context from HSA Compliance Guidelines v2.1:
      
      <chunk 1>
      Always use AES-256 encryption for PHI at rest...
      </chunk 1>
      
      <chunk 2>
      Use bcrypt (cost=12) for password hashing...
      </chunk 2>
      
      User Question: What's our HSA PHI redaction standard?
      
      Answer based on the context above:"
   
3. GENERATION
   - Send to LLM (GPT-4, Claude, etc.)
   - LLM generates response citing guidelines
   - Return to user with file:// link
```

**Example Response:**

```
According to **HSA Compliance Guidelines v2.1**:

> Always use AES-256 encryption for PHI at rest. Use bcrypt (cost=12) 
> for password hashing. Redact SSN/DOB in logs via regex pattern.

See: [HSA Compliance Guidelines](file:///docs/hsa-phi-redaction-standard.md)
```

---

## 🚫 What NOT to Do (RAG Anti-Patterns)

### ❌ Don't Over-Engineer

**SKIP these (overkill for CORTEX):**
- ❌ Pinecone/Weaviate (SQLite sufficient for 10K chunks)
- ❌ Hybrid search (keyword + semantic) - semantic alone works
- ❌ Re-ranking models (top-3 from all-MiniLM good enough)
- ❌ Query expansion (LLM does this implicitly)
- ❌ Multi-modal RAG (images/videos) - out of scope

**USE ONLY:**
- ✅ Sentence-transformers (embeddings)
- ✅ SQLite (storage)
- ✅ NumPy (similarity search)
- ✅ LangChain (text splitting only)

---

### ❌ Don't Skip Chunking Overlap

**Bad:**
```
Chunk 1: "Dogs are allowed in the office"
Chunk 2: "on Fridays only"  ← Missing context!
```

**Good:**
```
Chunk 1: "Dogs are allowed in the office on Fridays"
Chunk 2: "office on Fridays only. Maximum 2 dogs per..."
         ↑ 50-char overlap preserves context
```

---

### ❌ Don't Ignore Privacy

**Problem:** Embeddings can leak sensitive info.

**Solution:** Reuse CORTEX's existing privacy controls:
- ✅ Mark guidelines with `contains_phi`, `contains_pii`
- ✅ Block sharing via database triggers
- ✅ Audit log all guideline access
- ✅ Domain isolation via namespaces

---

### ❌ Don't Return Too Many Chunks

**Bad:** Return top 10 chunks → Overload LLM context

**Good:** Return top 3 chunks → Focused, relevant context

**Rule of Thumb:**
- 3 chunks × 400 chars = 1,200 chars (~300 tokens)
- Leaves room for prompt + response in LLM context window

---

## 🛠️ CORTEX Implementation Checklist

### Minimal RAG for Domain Guidelines

**Infrastructure (Week 6, Days 1-2):**
- ☐ Create `guidelines.db` with 2 tables:
  - `guideline_documents` (full docs)
  - `guideline_chunks` (embedded chunks)
- ☐ Install `sentence-transformers` (pip install)
- ☐ Install `langchain` (text splitting only)

**Core Engine (Week 6, Days 3-5):**
- ☐ Implement `GuidelineSimilarityEngine` class
  - Method: `ingest_guideline()` (chunk + embed + store)
  - Method: `search_guidelines()` (query → top 3 chunks)
- ☐ Integrate with existing `BrainInterface`

**CLI (Week 7, Day 1):**
- ☐ Command: `cortex guideline add --file doc.md --domain hsa`
- ☐ Command: `cortex guideline search "PHI redaction"`

**Integration (Week 7, Days 2-5):**
- ☐ Update intent router to detect guideline queries
- ☐ Augment LLM prompts with guideline chunks
- ☐ Add file:// citation links to responses

**Testing (Week 8):**
- ☐ Unit tests: chunking, embedding, search
- ☐ Integration tests: end-to-end query workflow
- ☐ Validation: HSA/FSA pilot teams test with real guidelines

---

## 📊 Performance Expectations

**Ingestion (One-Time):**
- 50-page doc → ~200 chunks → 10 seconds
- **User Impact:** Minimal (only during upload)

**Query (Real-Time):**
- Embed query: 50ms
- Search 3,000 chunks: 100ms
- Total: 150ms
- **User Impact:** Sub-200ms (excellent UX)

**Storage:**
- 150 guideline docs × 200KB avg = 30MB
- **User Impact:** Negligible

**Memory:**
- Sentence-transformers model: 90MB (loaded once at startup)
- **User Impact:** Minimal (~100MB total)

---

## 🎓 Key Takeaways

1. **RAG is about augmenting prompts with relevant documents**
   - Not about training models (that's fine-tuning)
   - Not about replacing LLMs (that's knowledge graphs)

2. **CORTEX already does 80% of RAG**
   - Tier 2 brain = Knowledge store
   - Pattern search = Retrieval
   - Context injection = Augmentation
   - LLM responses = Generation

3. **The 20% gap is semantic search**
   - CORTEX uses keyword matching
   - RAG uses embedding similarity
   - **Solution:** Add sentence-transformers

4. **Keep it simple**
   - SQLite (not Pinecone)
   - Sentence-transformers (not OpenAI embeddings)
   - Top-3 chunks (not re-ranking)
   - **Rationale:** 80/20 rule - simple covers 80% of use cases

5. **Privacy is non-negotiable**
   - Reuse CORTEX's existing multi-domain isolation
   - Default private (opt-in sharing)
   - PII/PHI/PCI hard-blocked
   - **Rationale:** Compliance first, convenience second

---

## 📚 Further Reading

**RAG Fundamentals:**
- Video: `docs/.library/RAG.md` (transcript of RAG crash course)
- Paper: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al.)

**Sentence Transformers:**
- Docs: https://www.sbert.net/
- Model: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

**LangChain Text Splitters:**
- Docs: https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/

**CORTEX 4.0 Architecture:**
- Master Plan: `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md`
- Section: 2.1 Multi-Domain Architecture (lines 1026-1250)

---

**Author:** Asif Hussain  
**Date:** December 18, 2025  
**Status:** ✅ APPROVED FOR CORTEX 4.0 IMPLEMENTATION
