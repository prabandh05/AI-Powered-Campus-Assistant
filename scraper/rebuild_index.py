"""
Rebuild the FAISS index from cleaned campus data.
Run this once to train the RAG properly.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.rag_engine import RAGEngine

def main():
    rag = RAGEngine()
    
    clean_path = "data/campus_clean.txt"
    if not os.path.exists(clean_path):
        print(f"[ERROR] {clean_path} not found! Run clean_data.py first.")
        return
    
    # Full rebuild on cleaned data
    rag.build_full_index(clean_path)
    
    # Verify with test queries
    print("\n" + "=" * 60)
    print("VERIFICATION TEST QUERIES")
    print("=" * 60)
    
    test_queries = [
        "Who is the principal of DSCE?",
        "What are the placement statistics?",
        "Tell me about CSE department",
        "What are the admission requirements?",
        "Tell me about the campus facilities",
        "What is the address of DSCE?",
        "What departments are available?",
        "How is the examination conducted?",
        "What about hostel facilities?",
        "Tell me about research at DSCE",
    ]
    
    for q in test_queries:
        results = rag.search(q, top_k=3)
        print(f"\n🔍 Q: {q}")
        if results:
            for i, r in enumerate(results):
                # Show first 200 chars of each result
                print(f"   [{i+1}] {r[:200]}...")
        else:
            print("   [NO RESULTS]")


if __name__ == "__main__":
    main()
