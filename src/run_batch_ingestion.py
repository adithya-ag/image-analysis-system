"""
Run Batch Ingestion - Multi-Model Support

Process images with CLIP or MobileCLIP.

Phase 1 Day 2 - Image Analysis System v0.1

Usage:
    python run_batch_ingestion.py --model clip
    python run_batch_ingestion.py --model mobileclip
"""

import sys
import os
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from config import Config
from ingestion.batch_processor import BatchProcessor, get_image_files


def main():
    """Main entry point for batch ingestion"""
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Batch image ingestion')
    parser.add_argument('--model', type=str, default='clip', 
                       choices=['clip', 'mobileclip'],
                       help='Model to use (default: clip)')
    parser.add_argument('--skip-existing', action='store_true',
                       help='Skip images already in database')
    parser.add_argument('--no-confirm', action='store_true',
                       help='Skip confirmation prompt')
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🖼️  IMAGE ANALYSIS SYSTEM - BATCH INGESTION")
    print("=" * 70)
    print(f"Model: {args.model.upper()}")
    print("=" * 70)
    
    # Initialize configuration
    config = Config(model_name=args.model)
    
    # Get all image files
    image_dir = config.data_dir / 'test_images'
    print(f"\n📂 Scanning directory: {image_dir}")
    
    if not image_dir.exists():
        print(f"❌ Error: Directory not found: {image_dir}")
        sys.exit(1)
    
    image_files = get_image_files(str(image_dir))
    
    if not image_files:
        print(f"❌ Error: No images found in {image_dir}")
        sys.exit(1)
    
    print(f"✅ Found {len(image_files)} images")
    
    # Show first few files
    print("\nFirst 5 images:")
    for i, path in enumerate(image_files[:5], 1):
        print(f"   {i}. {os.path.basename(path)}")
    if len(image_files) > 5:
        print(f"   ... and {len(image_files) - 5} more")
    
    # Confirm before processing
    print(f"\n⚠️  About to process {len(image_files)} images")
    print(f"   Model: {args.model}")
    print(f"   Skip existing: {args.skip_existing}")
    print(f"   Database: {config.lance_path.name}")
    
    if not args.no_confirm:
        response = input("\nContinue? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("❌ Cancelled by user")
            sys.exit(0)
    
    # Initialize processor
    processor = BatchProcessor(config)
    
    try:
        # Initialize (load model, connect to databases)
        processor.initialize()
        
        # Process images
        metrics = processor.process_images(image_files, skip_existing=args.skip_existing)
        
        # Print summary
        processor.print_summary()
        
        # Verify results
        success, stats = processor.verify_results()
        
        # Final status
        if success and metrics['failed'] == 0:
            print("\n🎉 BATCH INGESTION COMPLETED SUCCESSFULLY!")
            print(f"\nResults stored in:")
            print(f"   SQLite: {config.sqlite_path}")
            print(f"   LanceDB: {config.lance_path}")
            print("\nNext steps:")
            print(f"   1. Verify: python src/verify_batch.py")
            print(f"   2. Compare models: python compare_models.py")
            sys.exit(0)
        else:
            print("\n⚠️  BATCH INGESTION COMPLETED WITH WARNINGS")
            if metrics['failed'] > 0:
                print(f"   - {metrics['failed']} images failed to process")
            if not success:
                print(f"   - Database counts don't match")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        processor.print_summary()
        print("\nYou can resume by running this script again with --skip-existing")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        processor.cleanup()


if __name__ == '__main__':
    main()
