import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import ollama


class DocumentationGenerator:
    def __init__(self, repo_path: str, output_dir: str = "docs"):
        """
        Initialize the documentation generator.
        
        Args:
            repo_path: Path to the source code repository
            output_dir: Directory where documentation will be saved
        """
        self.repo_path = Path(repo_path).expanduser().absolute()
        self.output_dir = Path(output_dir).absolute()
        self.output_dir.mkdir(exist_ok=True)
        
        # Common documentation files to generate
        self.doc_files = {
            "getting-started.md": "Generate a comprehensive 'Getting Started' guide for this project. Include: "
                                "1. Prerequisites and system requirements\n"
                                "2. Installation instructions\n"
                                "3. Basic configuration\n"
                                "4. Running a simple example\n"
                                "5. Where to go next",
            
            "faq.md": "Create a Frequently Asked Questions document for this project. Include: "
                     "1. Common installation issues\n"
                     "2. Configuration problems\n"
                     "3. Usage questions\n"
                     "4. Troubleshooting tips\n"
                     "5. Community resources",
            
            "contributing.md": "Generate a contribution guide for this project. Include: "
                               "1. How to report issues\n"
                               "2. Pull request process\n"
                               "3. Coding standards\n"
                               "4. Testing requirements\n"
                               "5. Documentation guidelines",
            
            "reference.md": "Create a technical reference document for this project. Include: "
                           "1. API documentation\n"
                           "2. Configuration options\n"
                           "3. Command-line interface reference\n"
                           "4. File formats and data structures\n"
                           "5. Architectural overview",
            
            "algorithm.md": "Generate documentation about the algorithms used in this project. Include: "
                           "1. Key algorithms implemented\n"
                           "2. Mathematical foundations\n"
                           "3. Performance characteristics\n"
                           "4. Optimization techniques\n"
                           "5. References to academic papers",
            
            "features.md": "Create a features overview document for this project. Include: "
                          "1. Main features and capabilities\n"
                          "2. Comparison with similar projects\n"
                          "3. Use cases\n"
                          "4. Limitations\n"
                          "5. Roadmap and future features"
        }
    
    def analyze_repo(self) -> Dict:
        """
        Analyze the repository structure and content to provide context for documentation.
        
        Returns:
            Dictionary containing repo metadata and important files
        """
        repo_info = {
            "path": str(self.repo_path),
            "files": [],
            "readme": None,
            "license": None,
            "language_stats": {}
        }
        
        # Get top-level files
        for item in self.repo_path.iterdir():
            if item.is_file():
                repo_info["files"].append(item.name)
                if item.name.lower().startswith("readme"):
                    repo_info["readme"] = item.read_text(encoding="utf-8", errors="ignore")
                if item.name.lower() == "license":
                    repo_info["license"] = item.read_text(encoding="utf-8", errors="ignore")
        
        # Get language statistics (requires git)
        try:
            result = subprocess.run(
                ["git", "-C", str(self.repo_path), "ls-files"],
                capture_output=True, text=True, check=True
            )
            files = result.stdout.splitlines()
            extensions = {}
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext:
                    extensions[ext] = extensions.get(ext, 0) + 1
            repo_info["language_stats"] = extensions
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return repo_info
    
    def generate_with_ollama(self, prompt: str, context: str = "", model: str = "llama3.2:3b") -> str:
        """
        Generate documentation using Ollama with the specified model.
        
        Args:
            prompt: The main prompt for documentation generation
            context: Additional context about the project
            model: The Ollama model to use (default: deepseek)
            
        Returns:
            Generated documentation content
        """
        full_prompt = f"""
        You are an expert technical writer documenting a software project.
        Context about the project:
        {context}
        
        Please generate comprehensive documentation based on the following request:
        {prompt}
        
        The documentation should be:
        - Well-structured with clear headings
        - Written in Markdown format
        - Technical but accessible
        - Complete with examples where appropriate
        - Accurate to the best of your knowledge
        """
        
        try:
                        
            # Call Ollama via subprocess
            result = ollama.generate(
                model=model,
                prompt=full_prompt,
                stream=False
            )
            
            # Parse the response
            response = result['response']
            return response
        
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error generating documentation with Ollama: {str(e)}")
            return f"# Documentation Generation Error\n\nFailed to generate content: {str(e)}"
    
    def generate_all_docs(self) -> None:
        """
        Generate all documentation files for the project.
        """
        repo_info = self.analyze_repo()
        context = f"""
        Project located at: {repo_info['path']}
        Key files: {', '.join(repo_info['files'])}
        Primary languages: {', '.join(repo_info['language_stats'].keys())}
        
        README content:
        {repo_info['readme'] or 'No README found'}
        """
        
        print(f"Generating documentation for project at: {self.repo_path}")
        print(f"Output will be saved to: {self.output_dir}")
        
        for filename, prompt in self.doc_files.items():
            output_path = self.output_dir / filename
            print(f"Generating {filename}...")
            
            content = self.generate_with_ollama(prompt, context)
            
            # Save the generated content
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"Saved {output_path}")
        
        print("Documentation generation complete!")
    
    def generate_single_doc(self, filename: str, custom_prompt: Optional[str] = None) -> None:
        """
        Generate a single documentation file.
        
        Args:
            filename: Name of the documentation file to generate
            custom_prompt: Optional custom prompt to use instead of the default
        """
        if filename not in self.doc_files and not custom_prompt:
            raise ValueError(f"Unknown documentation file: {filename}. Provide a custom prompt.")
        
        repo_info = self.analyze_repo()
        context = f"""
        Project located at: {repo_info['path']}
        Key files: {', '.join(repo_info['files'])}
        Primary languages: {', '.join(repo_info['language_stats'].keys())}
        
        README content:
        {repo_info['readme'] or 'No README found'}
        """
        
        prompt = custom_prompt if custom_prompt else self.doc_files[filename]
        output_path = self.output_dir / filename
        
        print(f"Generating {filename}...")
        content = self.generate_with_ollama(prompt, context)
        
        # Save the generated content
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Saved {output_path}")


if __name__ == "__main__":
    import argparse

    
    parser = argparse.ArgumentParser(description="Generate documentation for a project using Ollama with DeepSeek model.")
    parser.add_argument("repo_path", help="Path to the source code repository")
    parser.add_argument("--output", "-o", default="docs", help="Output directory for documentation")
    parser.add_argument("--file", "-f", help="Generate a specific documentation file")
    parser.add_argument("--prompt", "-p", help="Custom prompt for single file generation")
    
    args = parser.parse_args()
    
    generator = DocumentationGenerator(args.repo_path, args.output)
    
    if args.file:
        generator.generate_single_doc(args.file, args.promt)
    else:
        generator.generate_all_docs()