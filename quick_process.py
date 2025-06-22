#!/usr/bin/env python3
"""
Quick Document Processor for EduAgent AI
Use this when the web interface hangs on "Processing uploaded content..."
"""

import asyncio
import sys
from pathlib import Path
from simple_document_processor import SimpleDocumentProcessor

async def main():
    if len(sys.argv) < 2:
        print("🎓 EduAgent AI - Quick Document Processor")
        print("=" * 50)
        print("Usage: python quick_process.py <file_path> [duration_minutes]")
        print()
        print("Examples:")
        print("  python quick_process.py my_lecture.pdf")
        print("  python quick_process.py diagram.png 2.0")
        print()
        print("Supported formats: PDF, PNG, JPG, JPEG")
        return
    
    file_path = sys.argv[1]
    duration = float(sys.argv[2]) if len(sys.argv) > 2 else 1.5
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    print("🎓 EduAgent AI - Quick Document Processor")
    print("=" * 50)
    print(f"📄 Processing: {file_path}")
    print(f"⏱️ Target duration: {duration} minutes")
    print()
    
    processor = SimpleDocumentProcessor()
    
    print("🔍 Extracting content...")
    result = await processor.process_document(file_path, duration)
    
    if result["success"]:
        print("✅ Processing complete!")
        print(f"📁 Output saved to: {result['output_path']}")
        print(f"⏱️ Processing time: {result['processing_time']}")
        print()
        print("📝 Generated Content Preview:")
        print("-" * 30)
        # Show first few lines of content
        preview = result["content"][:300] + "..." if len(result["content"]) > 300 else result["content"]
        print(preview)
        print()
        print("💡 Full content saved to output file!")
    else:
        print(f"❌ Processing failed: {result['error']}")

if __name__ == "__main__":
    asyncio.run(main())