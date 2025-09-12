#!/usr/bin/env python3
"""
AI Document Generator - Unified tool for generating various types of documentation
using Ollama with Llama3 model and other AI tools.

Features:
- README Generator
- Technical Documentation
- Blog Post Generator
- Haiku Writer
- Notes Writer
- Marp Slides Generator
- MOOC Creator
- Quiz Generator
"""

import argparse
import json
import os
import sys
import subprocess
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

class AIDocGenerator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model = "llama3.2:1b"
        self.output_dir = Path("./output")
        self.output_dir.mkdir(exist_ok=True)
        
        # Task configurations with specific prompts
        self.tasks = {
            "readme": {
                "name": "README Generator",
                "description": "Generate comprehensive README.md files",
                "output_format": "markdown",
                "extension": ".md"
            },
            "docs": {
                "name": "Documentation Generator", 
                "description": "Create technical documentation",
                "output_format": "markdown",
                "extension": ".md"
            },
            "blog": {
                "name": "Blog Post Generator",
                "description": "Generate engaging blog posts",
                "output_format": "markdown", 
                "extension": ".md"
            },
            "haiku": {
                "name": "Haiku Writer",
                "description": "Create beautiful haiku poems",
                "output_format": "text",
                "extension": ".txt"
            },
            "notes": {
                "name": "Notes Writer",
                "description": "Generate structured notes",
                "output_format": "markdown",
                "extension": ".md"
            },
            "slides": {
                "name": "Marp Slides Generator",
                "description": "Create Marp presentation slides",
                "output_format": "marp",
                "extension": ".md"
            },
            "mooc": {
                "name": "MOOC Creator",
                "description": "Generate online course content",
                "output_format": "structured",
                "extension": ".md"
            },
            "quiz": {
                "name": "Quiz Generator",
                "description": "Create interactive quizzes",
                "output_format": "json",
                "extension": ".json"
            }
        }

    def check_ollama_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def check_model_availability(self) -> bool:
        """Check if the specified model is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            models = response.json().get("models", [])
            return any(self.model in model["name"] for model in models)
        except:
            return False

    def call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """Make API call to Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                stream=True,
                timeout=120
            )
            if response.status_code == 200:
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode("utf-8"))
                            full_response += chunk.get("response", "")
                        except Exception:
                            continue
                return full_response
            elif response.status_code == 404:
                print("\n❌ Ollama API returned 404 Not Found for /api/generate.")
                print("Possible causes:")
                print("- Ollama server is running an older version (update Ollama)")
                print("- The endpoint URL is incorrect")
                print("- The model name is not available or not pulled")
                print("- The API route has changed")
                print("Run 'Debug Ollama Setup' from the interactive menu for more details.\n")
                raise Exception(f"Ollama API error: 404 - {response.text}")
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"Failed to call Ollama: {str(e)}")

    def get_task_specific_prompt(self, task: str, inputs: Dict[str, Any]) -> tuple:
        """Generate task-specific prompts"""
        
        prompts = {
            "readme": {
                "system": "You are an expert technical writer specializing in creating comprehensive, well-structured README files for software projects.",
                "template": """Create a comprehensive README.md for a project with the following details:

Project Name: {project_name}
Description: {description}
Technology Stack: {tech_stack}
Target Audience: {target_audience}

Include the following sections:
- Project title and description
- Installation instructions
- Usage examples
- Configuration options
- Contributing guidelines
- License information
- Contact/support information

Make it professional, clear, and engaging."""
            },
            
            "docs": {
                "system": "You are a technical documentation expert who creates clear, comprehensive, and well-organized documentation.",
                "template": """Create technical documentation for:

Topic: {topic}
Target Audience: {audience}
Complexity Level: {complexity}
Specific Areas to Cover: {areas}

Structure the documentation with:
- Clear headings and subheadings
- Code examples where relevant
- Best practices
- Common pitfalls
- References and further reading

Make it thorough yet accessible."""
            },
            
            "blog": {
                "system": "You are a skilled content writer who creates engaging, informative, and SEO-friendly blog posts.",
                "template": """Write a blog post about:

Topic: {topic}
Target Audience: {audience}
Tone: {tone}
Keywords to include: {keywords}
Estimated word count: {word_count}

Include:
- Compelling headline
- Engaging introduction
- Well-structured body with subheadings
- Practical examples or case studies
- Strong conclusion with call-to-action
- Meta description suggestion"""
            },
            
            "haiku": {
                "system": "You are a haiku master who creates beautiful, meaningful haiku poems following traditional 5-7-5 syllable structure.",
                "template": """Create haiku poems about:

Theme: {theme}
Mood: {mood}
Number of haikus: {count}
Style preference: {style}

Each haiku should:
- Follow 5-7-5 syllable pattern
- Capture a moment or feeling
- Include nature imagery when appropriate
- Evoke emotion or contemplation"""
            },
            
            "notes": {
                "system": "You are an expert note-taker who creates well-organized, comprehensive notes that are easy to review and understand.",
                "template": """Create structured notes for:

Subject: {subject}
Source material: {source}
Purpose: {purpose}
Format preference: {format}

Organize the notes with:
- Clear hierarchical structure
- Key concepts highlighted
- Important definitions
- Summary points
- Action items if applicable"""
            },
            
            "slides": {
                "system": "You are a presentation expert who creates engaging Marp slides with clear structure and visual appeal.",
                "template": """Create a Marp presentation about:

Topic: {topic}
Duration: {duration} minutes
Audience: {audience}
Number of slides: {slide_count}

Structure:
- Title slide
- Agenda/Overview
- Main content slides with clear points
- Conclusion/Summary
- Q&A slide

Use Marp markdown syntax with appropriate themes and styling."""
            },
            
            "mooc": {
                "system": "You are an instructional designer who creates comprehensive online course content with clear learning objectives.",
                "template": """Design a MOOC (Massive Open Online Course) for:

Course Title: {title}
Subject Area: {subject}
Target Level: {level}
Duration: {duration}
Learning Objectives: {objectives}

Create:
- Course overview and syllabus
- Module breakdowns with learning outcomes
- Lesson plans with activities
- Assessment strategies
- Resource recommendations
- Discussion prompts"""
            },
            
            "quiz": {
                "system": "You are an assessment expert who creates fair, comprehensive, and engaging quizzes that effectively test knowledge.",
                "template": """Create a quiz about:

Subject: {subject}
Difficulty Level: {difficulty}
Number of Questions: {question_count}
Question Types: {question_types}
Time Limit: {time_limit}

Include:
- Multiple choice questions
- True/false questions  
- Short answer questions
- Explanation for correct answers
- Difficulty progression
- Clear instructions"""
            }
        }
        
        if task not in prompts:
            raise ValueError(f"Unknown task: {task}")
            
        prompt_config = prompts[task]
        formatted_prompt = prompt_config["template"].format(**inputs)
        
        return prompt_config["system"], formatted_prompt

    def get_task_inputs(self, task: str) -> Dict[str, Any]:
        """Get task-specific inputs from user"""
        inputs = {}
        
        input_configs = {
            "readme": [
                ("project_name", "Enter project name: "),
                ("description", "Enter project description: "),
                ("tech_stack", "Enter technology stack (comma-separated): "),
                ("target_audience", "Enter target audience: ")
            ],
            "docs": [
                ("topic", "Enter documentation topic: "),
                ("audience", "Enter target audience: "),
                ("complexity", "Enter complexity level (beginner/intermediate/advanced): "),
                ("areas", "Enter specific areas to cover: ")
            ],
            "blog": [
                ("topic", "Enter blog post topic: "),
                ("audience", "Enter target audience: "),
                ("tone", "Enter desired tone (professional/casual/technical): "),
                ("keywords", "Enter SEO keywords (comma-separated): "),
                ("word_count", "Enter estimated word count: ")
            ],
            "haiku": [
                ("theme", "Enter haiku theme: "),
                ("mood", "Enter desired mood: "),
                ("count", "Enter number of haikus to generate: "),
                ("style", "Enter style preference (traditional/modern): ")
            ],
            "notes": [
                ("subject", "Enter subject/topic: "),
                ("source", "Enter source material: "),
                ("purpose", "Enter purpose of notes: "),
                ("format", "Enter preferred format (outline/detailed/summary): ")
            ],
            "slides": [
                ("topic", "Enter presentation topic: "),
                ("duration", "Enter presentation duration (minutes): "),
                ("audience", "Enter target audience: "),
                ("slide_count", "Enter approximate number of slides: ")
            ],
            "mooc": [
                ("title", "Enter course title: "),
                ("subject", "Enter subject area: "),
                ("level", "Enter target level (beginner/intermediate/advanced): "),
                ("duration", "Enter course duration: "),
                ("objectives", "Enter learning objectives: ")
            ],
            "quiz": [
                ("subject", "Enter quiz subject: "),
                ("difficulty", "Enter difficulty level: "),
                ("question_count", "Enter number of questions: "),
                ("question_types", "Enter question types (multiple choice, true/false, etc.): "),
                ("time_limit", "Enter time limit: ")
            ]
        }
        
        if task not in input_configs:
            return inputs
            
        print(f"\n=== {self.tasks[task]['name']} ===")
        for key, prompt in input_configs[task]:
            value = input(prompt).strip()
            inputs[key] = value if value else "Not specified"
            
        return inputs

    def save_output(self, content: str, task: str, filename: str = None) -> str:
        """Save generated content to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{task}_{timestamp}{self.tasks[task]['extension']}"
            
        filepath = self.output_dir / filename
        
        # Handle different output formats
        if self.tasks[task]["output_format"] == "json":
            try:
                # Try to parse and prettify JSON
                json_data = json.loads(content)
                content = json.dumps(json_data, indent=2)
            except:
                pass
                
        elif task == "slides":
            # Add Marp frontmatter if not present
            if not content.startswith("---"):
                marp_header = """---
marp: true
theme: default
paginate: true
---

"""
                content = marp_header + content
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return str(filepath)

    def interactive_mode(self):
        """Run in interactive mode"""
        print("🚀 AI Document Generator")
        print("=" * 50)
        
        # Check Ollama connection
        if not self.check_ollama_connection():
            print("❌ Error: Cannot connect to Ollama. Please ensure Ollama is running.")
            print("   Start Ollama with: ollama serve")
            return
            
        if not self.check_model_availability():
            print(f"❌ Error: Model '{self.model}' not found.")
            print(f"   Install with: ollama pull {self.model}")
            return
            
        print("✅ Connected to Ollama successfully!")
        
        while True:
            print("\nAvailable tasks:")
            for i, (key, task) in enumerate(self.tasks.items(), 1):
                print(f"{i}. {task['name']} - {task['description']}")
            print("9. Debug Ollama Setup")
            print("0. Exit")
            
            try:
                choice = input("\nSelect a task (0-9): ").strip()
                
                if choice == "0":
                    print("Goodbye! 👋")
                    break
                elif choice == "9":
                    self.debug_ollama()
                    continue
                    
                task_keys = list(self.tasks.keys())
                if choice.isdigit() and 1 <= int(choice) <= len(task_keys):
                    task = task_keys[int(choice) - 1]
                    self.process_task(task)
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\nExiting... 👋")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")

    def process_task(self, task: str):
        """Process a specific task"""
        try:
            print(f"\n🎯 Starting {self.tasks[task]['name']}...")
            
            # Get task-specific inputs
            inputs = self.get_task_inputs(task)
            
            # Generate prompts
            system_prompt, user_prompt = self.get_task_specific_prompt(task, inputs)
            
            print("\n🤖 Generating content with AI...")
            
            # Call AI model
            content = self.call_ollama(user_prompt, system_prompt)
            
            # Save output
            filepath = self.save_output(content, task)
            
            print(f"✅ Content generated successfully!")
            print(f"📁 Saved to: {filepath}")
            
            # Preview option
            preview = input("\nWould you like to preview the content? (y/n): ").lower()
            if preview == 'y':
                print("\n" + "=" * 80)
                print(content[:500] + ("..." if len(content) > 500 else ""))
                print("=" * 80)
                
        except Exception as e:
            print(f"❌ Error processing task: {str(e)}")

    def cli_mode(self, args):
        """Run in CLI mode"""
        if not self.check_ollama_connection():
            print("Error: Cannot connect to Ollama")
            sys.exit(1)
            
        if not self.check_model_availability():
            print(f"Error: Model '{self.model}' not available")
            sys.exit(1)
            
        try:
            # Parse inputs from CLI args or config file
            inputs = {}
            if args.config:
                with open(args.config, 'r') as f:
                    inputs = yaml.safe_load(f) if args.config.endswith('.yaml') else json.load(f)
            else:
                # Build inputs from CLI arguments
                inputs = {k: v for k, v in vars(args).items() 
                         if v is not None and k not in ['task', 'config', 'output']}
                         
            system_prompt, user_prompt = self.get_task_specific_prompt(args.task, inputs)
            content = self.call_ollama(user_prompt, system_prompt)
            
            filepath = self.save_output(content, args.task, args.output)
            print(f"Content generated: {filepath}")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

def main():
    generator = AIDocGenerator()
    
    parser = argparse.ArgumentParser(
        description="AI Document Generator - Create various types of documentation using AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Interactive mode
  %(prog)s readme --project-name "MyApp"      # Generate README
  %(prog)s blog --topic "AI in Healthcare"   # Generate blog post
  %(prog)s --config config.yaml readme       # Use config file
        """
    )
    
    parser.add_argument('task', nargs='?', choices=list(generator.tasks.keys()),
                       help='Task to perform')
    parser.add_argument('--config', help='Configuration file (JSON/YAML)')
    parser.add_argument('--output', help='Output filename')
    
    # Task-specific arguments
    parser.add_argument('--project-name', help='Project name (for README)')
    parser.add_argument('--description', help='Project description')
    parser.add_argument('--tech-stack', help='Technology stack')
    parser.add_argument('--target-audience', help='Target audience')
    parser.add_argument('--topic', help='Topic/subject')
    parser.add_argument('--audience', help='Target audience')
    parser.add_argument('--complexity', help='Complexity level')
    parser.add_argument('--tone', help='Writing tone')
    parser.add_argument('--keywords', help='SEO keywords')
    parser.add_argument('--word-count', help='Word count')
    parser.add_argument('--theme', help='Theme (for haiku)')
    parser.add_argument('--mood', help='Mood')
    parser.add_argument('--count', help='Number of items to generate')
    parser.add_argument('--style', help='Style preference')
    parser.add_argument('--subject', help='Subject/topic')
    parser.add_argument('--source', help='Source material')
    parser.add_argument('--purpose', help='Purpose')
    parser.add_argument('--format', help='Format preference')
    parser.add_argument('--duration', help='Duration')
    parser.add_argument('--slide-count', help='Number of slides')
    parser.add_argument('--title', help='Title')
    parser.add_argument('--level', help='Level (beginner/intermediate/advanced)')
    parser.add_argument('--objectives', help='Learning objectives')
    parser.add_argument('--difficulty', help='Difficulty level')
    parser.add_argument('--question-count', help='Number of questions')
    parser.add_argument('--question-types', help='Question types')
    parser.add_argument('--time-limit', help='Time limit')
    
    args = parser.parse_args()
    
    if args.task:
        generator.cli_mode(args)
    else:
        generator.interactive_mode()

if __name__ == "__main__":
    main()