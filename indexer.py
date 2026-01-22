import os
import json
import string
from rich.console import Console
from rich.progress import Progress

console = Console()

INDEX_FILE = "search_index.json"

# List of extensions we want to index
TEXT_EXTENSIONS = {
    '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yml', '.yaml', 
    '.sh', '.c', '.cpp', '.h', '.java', '.rs', '.go', '.ts'
}

# Directories to ignore
IGNORE_DIRS = {
    'venv', 'node_modules', '.git', '__pycache__', '.idea', '.vscode', 
    'dist', 'build', '.gemini'
}

def is_text_file(filename):
    return any(filename.lower().endswith(ext) for ext in TEXT_EXTENSIONS)

def tokenize(text):
    """
    Splits text into words, removes punctuation, and converts to lowercase.
    """
    # Replace punctuation with spaces to handle cases like "word1.word2" or "func('param')"
    translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    text = text.translate(translator)
    words = text.split()
    return set(word.lower() for word in words if word)

def count_files(root_dir):
    """Helper to count total files to be indexed for progress bar"""
    count = 0
    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
        for filename in filenames:
            if is_text_file(filename):
                count += 1
    return count

def build_index(root_dir):
    """
    Walks through the directory and builds an inverted index with line numbers.
    Returns: dict { word: { file_path: [line_numbers] } }
    """
    index = {}
    
    console.print(f"[bold blue]Scanning directory: {root_dir}[/bold blue]")
    
    # First pass: count files
    with console.status("[bold green]Counting files...[/bold green]"):
        total_files = count_files(root_dir)

    console.print(f"Found {total_files} files to index.")

    with Progress() as progress:
        task = progress.add_task("[cyan]Indexing...[/cyan]", total=total_files)

        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

            for filename in filenames:
                if is_text_file(filename):
                    path = os.path.join(dirpath, filename)
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            
                            file_words = {} # word -> list of line numbers
                            for i, line in enumerate(lines):
                                line_num = i + 1
                                words = tokenize(line)
                                for word in words:
                                    if word not in file_words:
                                        file_words[word] = []
                                    file_words[word].append(line_num)
                            
                            for word, line_nums in file_words.items():
                                if word not in index:
                                    index[word] = {}
                                index[word][path] = line_nums
                            
                            progress.advance(task)
                    except Exception as e:
                        console.print(f"[red]Error reading {path}: {e}[/red]")

    console.print(f"[green]Indexed {total_files} files.[/green]")
    return index

def save_index(index):
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f)
    console.print(f"[green]Index saved to {INDEX_FILE}[/green]")

def load_index():
    if not os.path.exists(INDEX_FILE):
        return None
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def search_index(query, index):
    """
    Searches for a query word in the index.
    Returns: dict { file_path: [line_numbers] }
    """
    query = query.lower().strip()
    return index.get(query, {})
