import subprocess
import sys
from pathlib import Path

def convert_markdown_to_pdf(md_file_path, output_path=None):
    """Convert markdown file to PDF using pandoc"""
    
    if output_path is None:
        output_path = md_file_path.with_suffix('.pdf')
    
    try:
        # Check if pandoc is installed
        subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Pandoc is not installed. Please install it first:")
        print("   macOS: brew install pandoc")
        print("   Ubuntu: sudo apt-get install pandoc")
        print("   Windows: Download from https://pandoc.org/installing.html")
        return False
    
    try:
        # Convert markdown to PDF
        cmd = [
            'pandoc',
            str(md_file_path),
            '-o', str(output_path),
            '--pdf-engine=xelatex',
            '--variable=geometry:margin=1in',
            '--variable=fontsize:11pt',
            '--variable=mainfont:DejaVu Sans',
            '--variable=monofont:DejaVu Sans Mono',
            '--toc',
            '--number-sections'
        ]
        
        print(f"🔄 Converting {md_file_path} to PDF...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PDF created: {output_path}")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def convert_html_to_pdf(html_file_path, output_path=None):
    """Convert HTML file to PDF using wkhtmltopdf"""
    
    if output_path is None:
        output_path = html_file_path.with_suffix('.pdf')
    
    try:
        # Check if wkhtmltopdf is installed
        subprocess.run(['wkhtmltopdf', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ wkhtmltopdf is not installed. Please install it first:")
        print("   macOS: brew install wkhtmltopdf")
        print("   Ubuntu: sudo apt-get install wkhtmltopdf")
        print("   Windows: Download from https://wkhtmltopdf.org/downloads.html")
        return False
    
    try:
        # Convert HTML to PDF
        cmd = [
            'wkhtmltopdf',
            '--page-size', 'A4',
            '--margin-top', '0.75in',
            '--margin-right', '0.75in',
            '--margin-bottom', '0.75in',
            '--margin-left', '0.75in',
            '--encoding', 'UTF-8',
            str(html_file_path),
            str(output_path)
        ]
        
        print(f"🔄 Converting {html_file_path} to PDF...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ PDF created: {output_path}")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Convert lecture files to PDF"""
    
    lectures_dir = Path("lectures")
    
    if not lectures_dir.exists():
        print("❌ Lectures directory not found")
        return
    
    # Find all markdown and HTML files
    md_files = list(lectures_dir.glob("*.md"))
    html_files = list(lectures_dir.glob("*.html"))
    
    print("📚 Found lecture files:")
    for md_file in md_files:
        print(f"   📝 {md_file.name}")
    for html_file in html_files:
        print(f"   🌐 {html_file.name}")
    
    print("\n🔄 Converting files to PDF...")
    
    # Convert markdown files
    for md_file in md_files:
        convert_markdown_to_pdf(md_file)
    
    # Convert HTML files
    for html_file in html_files:
        convert_html_to_pdf(html_file)
    
    print("\n✅ Conversion complete!")

if __name__ == "__main__":
    main() 