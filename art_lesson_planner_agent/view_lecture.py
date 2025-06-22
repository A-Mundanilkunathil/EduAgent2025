#!/usr/bin/env python3
"""
Lecture Viewer - View and render your generated lectures
"""

import os
import sys
import subprocess
from pathlib import Path

def list_lecture_files():
    """List all available lecture files"""
    lectures_dir = Path("lectures")
    
    if not lectures_dir.exists():
        print("❌ No lectures directory found. Generate a lecture first!")
        return []
    
    files = []
    
    # Find all lecture files
    for ext in ['*.md', '*.html', '*.json', '*.pdf']:
        files.extend(lectures_dir.glob(ext))
    
    return sorted(files)

def view_markdown(file_path):
    """View markdown file in terminal"""
    print(f"\n📝 Viewing: {file_path.name}")
    print("=" * 60)
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            print(content)
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def open_in_browser(file_path):
    """Open file in default browser"""
    try:
        subprocess.run(['open', str(file_path)], check=True)
        print(f"✅ Opened {file_path.name} in browser")
    except Exception as e:
        print(f"❌ Error opening in browser: {e}")

def open_in_editor(file_path):
    """Open file in default text editor"""
    try:
        subprocess.run(['open', str(file_path)], check=True)
        print(f"✅ Opened {file_path.name} in editor")
    except Exception as e:
        print(f"❌ Error opening in editor: {e}")

def show_file_info(file_path):
    """Show information about a file"""
    stat = file_path.stat()
    size_kb = stat.st_size / 1024
    
    print(f"\n📄 File: {file_path.name}")
    print(f"   Size: {size_kb:.1f} KB")
    print(f"   Type: {file_path.suffix}")
    print(f"   Modified: {stat.st_mtime}")

def main():
    """Main lecture viewer"""
    
    print("🎓 Lecture Viewer")
    print("=" * 40)
    
    # List available files
    files = list_lecture_files()
    
    if not files:
        print("❌ No lecture files found!")
        print("💡 Generate a lecture first using:")
        print("   python demo_lecture.py")
        print("   python comprehensive_lecture_generator.py")
        return
    
    print("📚 Available lecture files:")
    for i, file_path in enumerate(files, 1):
        show_file_info(file_path)
    
    print("\n🎯 Viewing Options:")
    print("1. View markdown in terminal")
    print("2. Open HTML in browser")
    print("3. Open in text editor")
    print("4. Convert to PDF")
    print("5. List all files")
    print("6. Exit")
    
    while True:
        try:
            choice = input("\nSelect option (1-6): ").strip()
            
            if choice == '1':
                # Find markdown files
                md_files = [f for f in files if f.suffix == '.md']
                if md_files:
                    view_markdown(md_files[0])
                else:
                    print("❌ No markdown files found")
            
            elif choice == '2':
                # Find HTML files
                html_files = [f for f in files if f.suffix == '.html']
                if html_files:
                    open_in_browser(html_files[0])
                else:
                    print("❌ No HTML files found")
            
            elif choice == '3':
                # Open first file in editor
                if files:
                    open_in_editor(files[0])
                else:
                    print("❌ No files found")
            
            elif choice == '4':
                print("🔄 Converting to PDF...")
                subprocess.run([sys.executable, 'convert_to_pdf.py'])
            
            elif choice == '5':
                files = list_lecture_files()
                print("\n📚 Available lecture files:")
                for file_path in files:
                    show_file_info(file_path)
            
            elif choice == '6':
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-6.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 