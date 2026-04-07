"""
RAG (Retrieval-Augmented Generation) Service for Product Knowledge Base
Provides semantic search over product information to help answer customer queries.
"""

import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


@dataclass
class SearchResult:
    """Represents a single search result from the knowledge base"""
    content: str
    score: float
    metadata: Dict[str, Any]
    source: str


class RAGService:
    """
    RAG service that provides semantic search over product knowledge base.
    Uses sentence transformers for embeddings and FAISS for efficient similarity search.
    """

    def __init__(self, knowledge_base_path: str = None, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG service.

        Args:
            knowledge_base_path: Path to the product knowledge base JSON file
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = None
        self.index = None
        self.documents = []
        self.metadata = []

        # Set default knowledge base path
        if knowledge_base_path is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            knowledge_base_path = os.path.join(backend_dir, "data", "product_knowledge_base.json")

        self.knowledge_base_path = knowledge_base_path
        self.knowledge_base = None

        # Initialize the service
        self._load_model()
        self._load_knowledge_base()
        self._build_index()

    def _load_model(self):
        """Load the sentence transformer model for embeddings"""
        print(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        print("Embedding model loaded successfully")

    def _load_knowledge_base(self):
        """Load the product knowledge base from JSON file"""
        if not os.path.exists(self.knowledge_base_path):
            raise FileNotFoundError(f"Knowledge base not found at: {self.knowledge_base_path}")

        with open(self.knowledge_base_path, 'r') as f:
            self.knowledge_base = json.load(f)

        print(f"Loaded knowledge base for: {self.knowledge_base.get('company', 'Unknown')}")

    def _build_index(self):
        """Build FAISS index from the knowledge base"""
        print("Building search index...")

        # Extract searchable content from knowledge base
        self._extract_documents()

        # Generate embeddings for all documents
        embeddings = self.model.encode(self.documents, show_progress_bar=True)

        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product (cosine similarity with normalized vectors)

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)

        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))

        print(f"Index built with {len(self.documents)} documents")

    def _extract_documents(self):
        """Extract searchable documents from the knowledge base"""
        self.documents = []
        self.metadata = []

        # Add company overview
        company_name = self.knowledge_base.get('company', '')
        self.documents.append(f"Company: {company_name}")
        self.metadata.append({
            'type': 'company_info',
            'company': company_name
        })

        # Process each product
        for product in self.knowledge_base.get('products', []):
            product_name = product.get('name', '')
            product_desc = product.get('description', '')

            # Add product overview
            self.documents.append(f"Product: {product_name}. {product_desc}")
            self.metadata.append({
                'type': 'product',
                'product_id': product.get('id', ''),
                'product_name': product_name
            })

            # Process each module
            for module in product.get('modules', []):
                module_name = module.get('name', '')
                module_desc = module.get('description', '')

                # Add module overview
                module_text = f"Module: {module_name} (part of {product_name}). {module_desc}"
                self.documents.append(module_text)
                self.metadata.append({
                    'type': 'module',
                    'product_name': product_name,
                    'module_id': module.get('id', ''),
                    'module_name': module_name
                })

                # Add features
                features = module.get('features', [])
                if features:
                    features_text = f"{module_name} features: " + "; ".join(features)
                    self.documents.append(features_text)
                    self.metadata.append({
                        'type': 'features',
                        'product_name': product_name,
                        'module_name': module_name,
                        'features': features
                    })

                # Add license information
                for license in module.get('licenses', []):
                    tier = license.get('tier', '')
                    price = license.get('price', '')
                    limits = license.get('limits', '')
                    support = license.get('support', '')
                    extras = license.get('extras', '')

                    license_text = (
                        f"{module_name} {tier} tier: {price}. "
                        f"Limits: {limits}. Support: {support}."
                    )
                    if extras:
                        license_text += f" Extras: {extras}."

                    self.documents.append(license_text)
                    self.metadata.append({
                        'type': 'license',
                        'product_name': product_name,
                        'module_name': module_name,
                        'tier': tier,
                        'price': price,
                        'limits': limits,
                        'support': support,
                        'extras': extras
                    })

        # Add common questions
        for qa in self.knowledge_base.get('common_questions', []):
            question = qa.get('question', '')
            answer = qa.get('answer', '')

            qa_text = f"Q: {question} A: {answer}"
            self.documents.append(qa_text)
            self.metadata.append({
                'type': 'faq',
                'question': question,
                'answer': answer
            })

        # Add pricing bundles
        for bundle in self.knowledge_base.get('pricing_bundles', []):
            bundle_name = bundle.get('name', '')
            bundle_desc = bundle.get('description', '')
            includes = bundle.get('includes', [])

            bundle_text = (
                f"Bundle: {bundle_name}. {bundle_desc}. "
                f"Includes: {', '.join(includes)}."
            )
            self.documents.append(bundle_text)
            self.metadata.append({
                'type': 'bundle',
                'bundle_name': bundle_name,
                'description': bundle_desc,
                'includes': includes,
                'pricing': bundle.get('pricing', {})
            })

    def search(self, query: str, top_k: int = 5, score_threshold: float = 0.3) -> List[SearchResult]:
        """
        Search the knowledge base for relevant information.

        Args:
            query: The search query
            top_k: Number of top results to return
            score_threshold: Minimum similarity score (0-1) for results

        Returns:
            List of SearchResult objects
        """
        # Generate query embedding
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)

        # Search the index
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)

        # Prepare results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score >= score_threshold:
                results.append(SearchResult(
                    content=self.documents[idx],
                    score=float(score),
                    metadata=self.metadata[idx],
                    source="knowledge_base"
                ))

        return results

    def get_context_for_query(self, query: str, max_results: int = 3) -> str:
        """
        Get formatted context for a query to use in LLM prompts.

        Args:
            query: The user's question
            max_results: Maximum number of results to include in context

        Returns:
            Formatted context string
        """
        results = self.search(query, top_k=max_results)

        if not results:
            return "No relevant information found in the knowledge base."

        context_parts = ["Relevant product information:"]
        for i, result in enumerate(results, 1):
            context_parts.append(f"\n{i}. {result.content} (relevance: {result.score:.2f})")

        return "\n".join(context_parts)

    def answer_question(self, query: str) -> Dict[str, Any]:
        """
        Answer a customer question using the knowledge base.

        Args:
            query: The customer's question

        Returns:
            Dictionary with answer and supporting information
        """
        # First check if this matches a common question
        for qa in self.knowledge_base.get('common_questions', []):
            question = qa.get('question', '').lower()
            if query.lower() in question or question in query.lower():
                return {
                    'answer': qa.get('answer', ''),
                    'source': 'faq',
                    'confidence': 'high',
                    'question': qa.get('question', '')
                }

        # Otherwise, search for relevant information
        results = self.search(query, top_k=5)

        if not results:
            return {
                'answer': "I don't have specific information about that. Let me connect you with a sales representative who can help.",
                'source': 'none',
                'confidence': 'low'
            }

        # Build answer from top results
        top_result = results[0]

        # Format answer based on result type
        if top_result.metadata['type'] == 'license':
            meta = top_result.metadata
            answer = (
                f"For {meta['module_name']}, the {meta['tier']} tier costs {meta['price']}. "
                f"{meta['limits']}. You'll get {meta['support']}."
            )
            if meta.get('extras'):
                answer += f" Additional features include: {meta['extras']}."

        elif top_result.metadata['type'] == 'module':
            answer = top_result.content

            # Add features if available
            feature_results = [r for r in results if r.metadata.get('type') == 'features']
            if feature_results:
                features = feature_results[0].metadata.get('features', [])
                if features:
                    answer += f"\n\nKey features include:\n" + "\n".join([f"• {f}" for f in features[:5]])

        elif top_result.metadata['type'] == 'bundle':
            meta = top_result.metadata
            answer = f"{meta['bundle_name']}: {meta['description']}"
            if meta.get('pricing'):
                answer += "\n\nPricing: " + ", ".join([f"{k}: {v}" for k, v in meta['pricing'].items()])

        else:
            answer = top_result.content

        return {
            'answer': answer,
            'source': 'knowledge_base',
            'confidence': 'high' if top_result.score > 0.6 else 'medium',
            'results': [{'content': r.content, 'score': r.score} for r in results[:3]]
        }

    def get_product_info(self, product_name: str = None, module_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific product or module.

        Args:
            product_name: Name of the product
            module_name: Name of the module (optional)

        Returns:
            Product/module information dictionary
        """
        for product in self.knowledge_base.get('products', []):
            if product_name and product_name.lower() in product.get('name', '').lower():
                if module_name:
                    # Find specific module
                    for module in product.get('modules', []):
                        if module_name.lower() in module.get('name', '').lower():
                            return {
                                'product': product.get('name'),
                                'module': module
                            }
                else:
                    return product

        return None

    def list_all_products(self) -> List[Dict[str, str]]:
        """Get a list of all available products"""
        return [
            {
                'id': p.get('id', ''),
                'name': p.get('name', ''),
                'description': p.get('description', ''),
                'modules': [m.get('name', '') for m in p.get('modules', [])]
            }
            for p in self.knowledge_base.get('products', [])
        ]

    def get_pricing_for_module(self, module_name: str) -> Optional[List[Dict[str, Any]]]:
        """Get pricing information for a specific module"""
        for product in self.knowledge_base.get('products', []):
            for module in product.get('modules', []):
                if module_name.lower() in module.get('name', '').lower():
                    return module.get('licenses', [])

        return None


# Singleton instance
_rag_service_instance: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create the RAG service singleton instance"""
    global _rag_service_instance

    if _rag_service_instance is None:
        _rag_service_instance = RAGService()

    return _rag_service_instance


if __name__ == "__main__":
    # Test the RAG service
    print("Initializing RAG service...")
    rag = RAGService()

    # Test queries
    test_queries = [
        "What cloud monitoring solutions do you have?",
        "How much does the enterprise plan cost?",
        "Tell me about cost optimization features",
        "What's included in CloudOps Suite?",
        "Do you have ML capabilities?",
        "What's the pricing for the Professional tier?",
        "Can I get a trial?",
        "What security features are available?"
    ]

    print("\n" + "="*80)
    print("Testing RAG Service")
    print("="*80)

    for query in test_queries:
        print(f"\n\nQuery: {query}")
        print("-" * 80)

        result = rag.answer_question(query)
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Source: {result['source']}")
