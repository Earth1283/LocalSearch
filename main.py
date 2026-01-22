import os
import inquirer
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter
import indexer

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def handle_build_index():
    console.print("[cyan]Enter directory to index (Tab completion enabled):[/cyan]")
    
    completer = PathCompleter(only_directories=True, expanduser=True)
    directory = prompt("> ", completer=completer, default=".")
    
    directory = os.path.expanduser(directory)
    
    if not os.path.isdir(directory):
        console.print(f"[bold red]Directory '{directory}' does not exist.[/bold red]")
        return

    index = indexer.build_index(directory)
    indexer.save_index(index)
    console.print("[bold green]Indexing complete! Press Enter to continue...[/bold green]")
    input()

def display_snippets(filepath, line_numbers, query, context=2):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        console.print(f"\n[bold yellow]Matches in {filepath}:[/bold yellow]")
        
        # Track displayed lines to avoid overlaps
        displayed = set()
        
        for ln in line_numbers:
            start = max(0, ln - context - 1)
            end = min(len(lines), ln + context)
            
            # Check if this range has already been mostly covered
            if ln in displayed:
                continue
                
            console.print(f"[dim]--- Line {ln} ---[/dim]")
            for i in range(start, end):
                current_ln = i + 1
                line_text = lines[i].rstrip()
                if current_ln == ln:
                    console.print(f"[bold green]{current_ln:4}: {line_text}[/bold green]")
                else:
                    console.print(f"{current_ln:4}: {line_text}")
                displayed.add(current_ln)
            console.print()
            
    except Exception as e:
        console.print(f"[red]Error reading snippets: {e}[/red]")

def preview_file(filepath, query):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        ext = os.path.splitext(filepath)[1][1:]
        lexer = ext if ext else "text"
        
        syntax = Syntax(content, lexer, theme="monokai", line_numbers=True, highlight_lines={})
        console.print(Panel(syntax, title=f"Full View: {filepath}", subtitle=f"Search Query: {query}"))
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
    
    console.print("\n[dim]Press Enter to return to results...[/dim]")
    input()

def handle_search():
    index = indexer.load_index()
    if not index:
        console.print("[bold red]No index found. Please build the index first.[/bold red]")
        input()
        return

    questions = [
        inquirer.Text('query', message="Enter search term")
    ]
    answers = inquirer.prompt(questions)
    query = answers['query']
    
    # results is now { path: [line_nums] }
    results_dict = indexer.search_index(query, index)
    
    if not results_dict:
        console.print(f"[yellow]No results found for '{query}'.[/yellow]")
        input()
        return

    file_paths = list(results_dict.keys())

    while True:
        clear_screen()
        console.print(f"[bold blue]Found matches in {len(file_paths)} files for '{query}':[/bold blue]")
        
        choices = file_paths + ["<< Back to Main Menu"]
        
        selection_q = [
            inquirer.List('file',
                          message="Select a file to see snippets",
                          choices=choices,
                          carousel=True)
        ]
        
        answer = inquirer.prompt(selection_q)
        selection = answer['file']
        
        if selection == "<< Back to Main Menu":
            break
        
        clear_screen()
        line_nums = results_dict[selection]
        display_snippets(selection, line_nums, query)
        
        # After showing snippets, ask if they want full preview
        sub_q = [
            inquirer.List('sub_action',
                          message="Action:",
                          choices=['Full Preview', 'Back to Results'],
                          carousel=True)
        ]
        sub_answer = inquirer.prompt(sub_q)
        if sub_answer['sub_action'] == 'Full Preview':
            clear_screen()
            preview_file(selection, query)


def main():
    while True:
        clear_screen()
        console.print(Panel.fit("[bold cyan]Local Search Engine[/bold cyan]"))
        
        questions = [
            inquirer.List('action',
                          message="What would you like to do?",
                          choices=['Build Index', 'Search', 'Exit'],
                          carousel=True)
        ]
        
        answer = inquirer.prompt(questions)
        action = answer['action']
        
        if action == 'Exit':
            console.print("[green]Goodbye![/green]")
            break
        elif action == 'Build Index':
            handle_build_index()
        elif action == 'Search':
            handle_search()

if __name__ == "__main__":
    main()
