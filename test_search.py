"""
Test Search Functionality

Quick test to verify semantic search is working.
Tests with various queries and displays results.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from retrieval.search_engine import SearchEngine


def test_search(model_name='clip'):
    """
    Test search with sample queries.
    
    Args:
        model_name: Which model to test ('clip', 'mobileclip', 'siglip')
    """
    print(f"\n{'='*70}")
    print(f"TESTING SEARCH ENGINE - {model_name.upper()}")
    print(f"{'='*70}\n")
    
    # Initialize search engine
    try:
        engine = SearchEngine(model_name=model_name, db_path='databases')
    except Exception as e:
        print(f"❌ Failed to initialize search engine: {e}")
        return False
    
    # Test queries
    test_queries = [
        "beach sunset",
        "people indoors", 
        "nature landscape",
        "food",
        "building architecture"
    ]
    
    print(f"\nRunning {len(test_queries)} test queries...\n")
    
    all_passed = True
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}/{len(test_queries)}: '{query}'")
        print(f"{'─'*70}")
        
        try:
            # Search with top 5 results
            results = engine.search_and_display(query, top_k=5, verbose=True)
            
            if len(results) > 0:
                print(f"✅ Query '{query}' returned {len(results)} results")
            else:
                print(f"⚠️  Query '{query}' returned 0 results")
                all_passed = False
                
        except Exception as e:
            print(f"❌ Query '{query}' failed: {e}")
            all_passed = False
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*70}")
    if all_passed:
        print(f"✅ ALL TESTS PASSED for {model_name.upper()}")
    else:
        print(f"⚠️  SOME TESTS FAILED for {model_name.upper()}")
    print(f"{'='*70}\n")
    
    return all_passed


def main():
    """Run tests for all models or a specific model."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test search functionality')
    parser.add_argument('--model', type=str, default='all',
                       choices=['all', 'clip', 'mobileclip', 'siglip'],
                       help='Which model to test (default: all)')
    
    args = parser.parse_args()
    
    if args.model == 'all':
        # Test all models
        models = ['clip', 'mobileclip', 'siglip']
        results = {}
        
        for model in models:
            try:
                results[model] = test_search(model)
            except Exception as e:
                print(f"\n❌ {model.upper()} test failed with error: {e}")
                results[model] = False
        
        # Summary
        print(f"\n{'='*70}")
        print("FINAL SUMMARY")
        print(f"{'='*70}")
        for model, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{model.upper():15} {status}")
        print(f"{'='*70}\n")
    else:
        # Test single model
        test_search(args.model)


if __name__ == '__main__':
    main()
