"""
Compare Search Quality Across Models

Tests the same queries on all 3 models and compares:
- Result relevance (manual review)
- Search speed
- Result diversity
- Ranking quality
"""

import sys
import time
from pathlib import Path
from typing import List, Dict

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from retrieval.search_engine import SearchEngine


class SearchQualityComparison:
    """Compare search quality across multiple models."""
    
    def __init__(self, db_path='databases'):
        """Initialize comparison with all models."""
        self.db_path = db_path
        self.models = ['clip', 'mobileclip', 'siglip']
        self.engines = {}
        
        print("Initializing search engines...\n")
        for model in self.models:
            try:
                self.engines[model] = SearchEngine(model_name=model, db_path=db_path)
                print(f"✅ {model.upper()} ready")
            except Exception as e:
                print(f"❌ {model.upper()} failed: {e}")
        
        print()
    
    def compare_query(self, query: str, top_k: int = 10) -> Dict:
        """
        Compare search results for a query across all models.
        
        Args:
            query: Search query
            top_k: Number of results per model
            
        Returns:
            Dict with model names as keys, results and timing as values
        """
        print(f"\n{'='*70}")
        print(f"COMPARING QUERY: '{query}'")
        print(f"{'='*70}\n")
        
        comparison = {}
        
        for model in self.models:
            if model not in self.engines:
                print(f"⚠️  Skipping {model.upper()} (not initialized)")
                continue
            
            print(f"\n{model.upper()} Results:")
            print(f"{'-'*70}")
            
            # Time the search
            start_time = time.time()
            
            try:
                results = self.engines[model].search(query, top_k=top_k)
                search_time = time.time() - start_time
                
                # Display results
                print(f"Search time: {search_time:.3f}s")
                print(f"Results found: {len(results)}\n")
                
                for i, result in enumerate(results[:5], 1):  # Show top 5
                    print(f"{i}. Score: {result['score']:.4f} | {Path(result['file_path']).name}")
                
                comparison[model] = {
                    'results': results,
                    'search_time': search_time,
                    'count': len(results)
                }
                
            except Exception as e:
                print(f"❌ Search failed: {e}")
                comparison[model] = {
                    'results': [],
                    'search_time': 0,
                    'count': 0,
                    'error': str(e)
                }
        
        return comparison
    
    def compare_multiple_queries(self, queries: List[str], top_k: int = 10):
        """
        Compare search across multiple queries.
        
        Args:
            queries: List of search queries
            top_k: Number of results per query
        """
        all_comparisons = {}
        
        for query in queries:
            comparison = self.compare_query(query, top_k=top_k)
            all_comparisons[query] = comparison
        
        # Summary
        print(f"\n\n{'='*70}")
        print("SUMMARY - Average Performance")
        print(f"{'='*70}\n")
        
        # Calculate averages
        for model in self.models:
            if model not in self.engines:
                continue
                
            times = [c[model]['search_time'] for c in all_comparisons.values() 
                    if model in c and 'error' not in c[model]]
            counts = [c[model]['count'] for c in all_comparisons.values() 
                     if model in c and 'error' not in c[model]]
            
            if times:
                avg_time = sum(times) / len(times)
                avg_count = sum(counts) / len(counts)
                
                print(f"{model.upper():15}")
                print(f"  Avg search time: {avg_time:.3f}s")
                print(f"  Avg results:     {avg_count:.1f}")
                print()
        
        print(f"{'='*70}\n")
        
        return all_comparisons
    
    def detailed_comparison(self, query: str, top_k: int = 10):
        """
        Detailed side-by-side comparison for manual quality assessment.
        
        Args:
            query: Search query
            top_k: Number of results to compare
        """
        print(f"\n{'='*70}")
        print(f"DETAILED COMPARISON: '{query}'")
        print(f"{'='*70}\n")
        
        # Get results from all models
        all_results = {}
        for model in self.models:
            if model in self.engines:
                results = self.engines[model].search(query, top_k=top_k)
                all_results[model] = results
        
        # Side-by-side comparison
        print(f"{'Rank':<6} {'CLIP':<45} {'MobileCLIP':<45} {'SigLIP':<45}")
        print(f"{'-'*140}")
        
        for i in range(min(top_k, max(len(r) for r in all_results.values()))):
            rank_str = f"#{i+1}"
            
            row = [rank_str]
            for model in self.models:
                if model in all_results and i < len(all_results[model]):
                    result = all_results[model][i]
                    filename = Path(result['file_path']).name[:35]
                    score = result['score']
                    entry = f"{filename} ({score:.3f})"
                else:
                    entry = "-"
                row.append(entry)
            
            print(f"{row[0]:<6} {row[1]:<45} {row[2]:<45} {row[3]:<45}")
        
        print(f"{'-'*140}\n")
        
        # Result overlap analysis
        print("Result Overlap Analysis:")
        print("-" * 40)
        
        for model in self.models:
            if model in all_results:
                files = set(Path(r['file_path']).name for r in all_results[model][:5])
                
                for other_model in self.models:
                    if other_model != model and other_model in all_results:
                        other_files = set(Path(r['file_path']).name 
                                        for r in all_results[other_model][:5])
                        overlap = len(files & other_files)
                        print(f"{model.upper()} ∩ {other_model.upper()}: {overlap}/5 common in top 5")
        
        print()


def main():
    """Run search quality comparison."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare search quality across models')
    parser.add_argument('--queries', type=str, nargs='+',
                       default=["beach sunset", "people indoors", "nature", "food"],
                       help='Queries to test')
    parser.add_argument('--top-k', type=int, default=10,
                       help='Number of results per query')
    parser.add_argument('--detailed', type=str, default=None,
                       help='Query for detailed side-by-side comparison')
    
    args = parser.parse_args()
    
    # Initialize comparison
    comparison = SearchQualityComparison(db_path='databases')
    
    if args.detailed:
        # Detailed comparison for specific query
        comparison.detailed_comparison(args.detailed, top_k=args.top_k)
    else:
        # Compare multiple queries
        comparison.compare_multiple_queries(args.queries, top_k=args.top_k)
        
        # Ask if user wants detailed comparison
        print("\nFor detailed side-by-side comparison, run:")
        print(f"python compare_search_quality.py --detailed \"your query here\"")
        print()


if __name__ == '__main__':
    main()
