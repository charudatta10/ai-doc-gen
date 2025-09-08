#!/usr/bin/env python3
"""
MOOC Generator System with Ollama Integration
Generates complete MOOC courses with AI agents for content creation
"""

import json
import os
import asyncio
import aiohttp
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from datetime import datetime
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MOOCConfig:
    """Configuration for MOOC generation"""
    topic: str
    credits: int
    duration_weeks: int
    human_in_loop: bool = True
    ollama_host: str = "http://localhost:11434"
    base_model: str = "llama3.1"
    output_dir: str = "./mooc_output"
    
@dataclass
class Module:
    """Represents a course module"""
    id: str
    title: str
    description: str
    week: int
    learning_objectives: List[str]
    content_types: List[str]  # ['video', 'notes', 'quiz', 'assignment']
    
@dataclass
class Syllabus:
    """Course syllabus structure"""
    course_title: str
    credits: int
    duration_weeks: int
    description: str
    learning_outcomes: List[str]
    modules: List[Module]
    assessment_structure: Dict[str, float]
    references: List[str]

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host.rstrip('/')
        
    async def generate(self, model: str, prompt: str, system: str = None) -> str:
        """Generate text using Ollama"""
        url = f"{self.host}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        if system:
            payload["system"] = system
            
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', '')
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        return ""
            except Exception as e:
                logger.error(f"Error calling Ollama: {e}")
                return ""
    
    async def list_models(self) -> List[str]:
        """List available models"""
        url = f"{self.host}/api/tags"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        result = await response.json()
                        return [model['name'] for model in result.get('models', [])]
                    else:
                        return []
            except Exception as e:
                logger.error(f"Error listing models: {e}")
                return []

class AIAgent:
    """Base class for specialized AI agents"""
    
    def __init__(self, ollama_client: OllamaClient, model: str, role: str):
        self.ollama = ollama_client
        self.model = model
        self.role = role
        
    async def generate_content(self, prompt: str, context: str = None) -> str:
        """Generate content with role-specific system prompt"""
        system_prompt = f"You are an expert {self.role}. {context or ''}"
        return await self.ollama.generate(self.model, prompt, system_prompt)

class SyllabusAgent(AIAgent):
    """Agent specialized in creating course syllabi"""
    
    def __init__(self, ollama_client: OllamaClient, model: str):
        super().__init__(ollama_client, model, "curriculum designer and educational consultant")
    
    async def create_syllabus(self, topic: str, credits: int, duration_weeks: int) -> Syllabus:
        """Generate a complete syllabus"""
        
        prompt = f"""
        Create a comprehensive syllabus for a {credits}-credit course on "{topic}" 
        spanning {duration_weeks} weeks. Include:
        
        1. Course title and description
        2. Learning outcomes (4-6 outcomes)
        3. Weekly modules with titles and descriptions
        4. Learning objectives for each module
        5. Assessment structure (percentages for different components)
        6. Key references and resources
        
        Format the response as structured data that can be parsed.
        """
        
        context = """
        Focus on creating academically rigorous content suitable for higher education.
        Ensure proper progression of difficulty and comprehensive coverage of the topic.
        Include diverse assessment methods and current, relevant references.
        """
        
        response = await self.generate_content(prompt, context)
        return self._parse_syllabus_response(response, topic, credits, duration_weeks)
    
    def _parse_syllabus_response(self, response: str, topic: str, credits: int, duration_weeks: int) -> Syllabus:
        """Parse LLM response into Syllabus object"""
        # This is a simplified parser - in practice, you'd want more robust parsing
        lines = response.strip().split('\n')
        
        # Extract key information (this would need more sophisticated parsing)
        course_title = f"{topic} - {credits} Credit Course"
        description = "AI-generated course description"
        learning_outcomes = ["Outcome 1", "Outcome 2", "Outcome 3", "Outcome 4"]
        
        # Create modules based on weeks
        modules = []
        for week in range(1, duration_weeks + 1):
            module = Module(
                id=f"module_{week}",
                title=f"Week {week}: Module Title",
                description=f"Module description for week {week}",
                week=week,
                learning_objectives=[f"Learning objective {week}.1", f"Learning objective {week}.2"],
                content_types=['video', 'notes', 'quiz']
            )
            modules.append(module)
        
        assessment_structure = {
            "assignments": 0.4,
            "midterm": 0.2,
            "final": 0.25,
            "participation": 0.15
        }
        
        references = ["Reference 1", "Reference 2", "Reference 3"]
        
        return Syllabus(
            course_title=course_title,
            credits=credits,
            duration_weeks=duration_weeks,
            description=description,
            learning_outcomes=learning_outcomes,
            modules=modules,
            assessment_structure=assessment_structure,
            references=references
        )

class ContentAgent(AIAgent):
    """Agent specialized in creating educational content"""
    
    def __init__(self, ollama_client: OllamaClient, model: str):
        super().__init__(ollama_client, model, "educational content creator and instructional designer")
    
    async def create_lecture_notes(self, module: Module, syllabus: Syllabus) -> str:
        """Generate lecture notes for a module"""
        prompt = f"""
        Create comprehensive lecture notes for:
        Module: {module.title}
        Description: {module.description}
        Learning Objectives: {', '.join(module.learning_objectives)}
        
        The notes should be:
        - Well-structured with clear headings
        - Include examples and explanations
        - Approximately 2000-3000 words
        - Include key concepts, definitions, and practical applications
        - Reference relevant materials from the syllabus
        """
        
        context = f"""
        This is part of a {syllabus.credits}-credit course on {syllabus.course_title}.
        Ensure content aligns with overall course learning outcomes:
        {', '.join(syllabus.learning_outcomes)}
        """
        
        return await self.generate_content(prompt, context)
    
    async def create_video_script(self, module: Module, syllabus: Syllabus) -> str:
        """Generate video script for a module"""
        prompt = f"""
        Create a video script for:
        Module: {module.title}
        Description: {module.description}
        
        The script should:
        - Be 15-20 minutes long when spoken
        - Include clear transitions and engaging elements
        - Have speaker notes and visual cues
        - Be conversational but educational
        - Include pause points for reflection
        """
        
        context = f"This video is part of {syllabus.course_title}."
        
        return await self.generate_content(prompt, context)
    
    async def create_quiz(self, module: Module, syllabus: Syllabus) -> str:
        """Generate quiz questions for a module"""
        prompt = f"""
        Create a 10-question quiz for:
        Module: {module.title}
        Learning Objectives: {', '.join(module.learning_objectives)}
        
        Include:
        - 5 multiple choice questions
        - 3 short answer questions
        - 2 essay questions
        - Provide correct answers and explanations
        """
        
        return await self.generate_content(prompt)

class AssessmentAgent(AIAgent):
    """Agent specialized in creating assessments"""
    
    def __init__(self, ollama_client: OllamaClient, model: str):
        super().__init__(ollama_client, model, "educational assessment specialist")
    
    async def create_assignment(self, module: Module, syllabus: Syllabus) -> str:
        """Create assignment for a module"""
        prompt = f"""
        Create a comprehensive assignment for:
        Module: {module.title}
        Learning Objectives: {', '.join(module.learning_objectives)}
        
        The assignment should:
        - Test understanding of key concepts
        - Include both theoretical and practical components
        - Have clear rubric and grading criteria
        - Be appropriate for {syllabus.credits}-credit level
        """
        
        return await self.generate_content(prompt)

class MOOCGenerator:
    """Main class for coordinating MOOC generation"""
    
    def __init__(self, config: MOOCConfig):
        self.config = config
        self.ollama = OllamaClient(config.ollama_host)
        
        # Initialize AI agents
        self.syllabus_agent = SyllabusAgent(self.ollama, config.base_model)
        self.content_agent = ContentAgent(self.ollama, config.base_model)
        self.assessment_agent = AssessmentAgent(self.ollama, config.base_model)
        
        # Create output directory
        self.output_path = Path(config.output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)
    
    async def generate_mooc(self) -> Dict:
        """Generate complete MOOC"""
        logger.info(f"Starting MOOC generation for: {self.config.topic}")
        
        # Step 1: Generate syllabus
        logger.info("Generating syllabus...")
        syllabus = await self.syllabus_agent.create_syllabus(
            self.config.topic, 
            self.config.credits, 
            self.config.duration_weeks
        )
        
        if self.config.human_in_loop:
            syllabus = await self._review_syllabus(syllabus)
        
        # Step 2: Generate content for each module
        logger.info("Generating module content...")
        module_content = {}
        
        for module in syllabus.modules:
            logger.info(f"Processing {module.title}")
            
            content = {}
            
            # Generate lecture notes
            if 'notes' in module.content_types:
                content['notes'] = await self.content_agent.create_lecture_notes(module, syllabus)
            
            # Generate video script
            if 'video' in module.content_types:
                content['video_script'] = await self.content_agent.create_video_script(module, syllabus)
            
            # Generate quiz
            if 'quiz' in module.content_types:
                content['quiz'] = await self.content_agent.create_quiz(module, syllabus)
            
            # Generate assignment
            if 'assignment' in module.content_types:
                content['assignment'] = await self.assessment_agent.create_assignment(module, syllabus)
            
            module_content[module.id] = content
        
        # Step 3: Save all content
        await self._save_mooc_content(syllabus, module_content)
        
        return {
            "syllabus": asdict(syllabus),
            "modules": module_content,
            "status": "completed",
            "output_directory": str(self.output_path)
        }
    
    async def _review_syllabus(self, syllabus: Syllabus) -> Syllabus:
        """Human-in-the-loop syllabus review"""
        print("\n" + "="*50)
        print("SYLLABUS REVIEW")
        print("="*50)
        print(f"Course: {syllabus.course_title}")
        print(f"Credits: {syllabus.credits}")
        print(f"Duration: {syllabus.duration_weeks} weeks")
        print(f"Description: {syllabus.description}")
        print("\nLearning Outcomes:")
        for i, outcome in enumerate(syllabus.learning_outcomes, 1):
            print(f"  {i}. {outcome}")
        
        print("\nModules:")
        for module in syllabus.modules:
            print(f"  Week {module.week}: {module.title}")
        
        approve = input("\nApprove this syllabus? (y/n): ").lower().strip()
        
        if approve == 'y':
            return syllabus
        else:
            # In a real implementation, you'd allow editing
            print("Syllabus editing not implemented in this demo.")
            return syllabus
    
    async def _save_mooc_content(self, syllabus: Syllabus, module_content: Dict):
        """Save all generated content to files"""
        
        # Save syllabus
        syllabus_file = self.output_path / "syllabus.yaml"
        with open(syllabus_file, 'w') as f:
            yaml.dump(asdict(syllabus), f, default_flow_style=False)
        
        # Save module content
        for module_id, content in module_content.items():
            module_dir = self.output_path / module_id
            module_dir.mkdir(exist_ok=True)
            
            for content_type, content_data in content.items():
                file_ext = {
                    'notes': 'md',
                    'video_script': 'md',
                    'quiz': 'md',
                    'assignment': 'md'
                }.get(content_type, 'txt')
                
                content_file = module_dir / f"{content_type}.{file_ext}"
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(content_data)
        
        logger.info(f"MOOC content saved to: {self.output_path}")

class MOOCInterface:
    """User interface for MOOC generation"""
    
    @staticmethod
    def get_user_input() -> MOOCConfig:
        """Get configuration from user input"""
        print("MOOC Generator")
        print("="*40)
        
        topic = input("Enter course topic: ").strip()
        
        while True:
            try:
                credits = int(input("Enter number of credits (2, 3, or 4): "))
                if credits in [2, 3, 4]:
                    break
                else:
                    print("Please enter 2, 3, or 4 credits.")
            except ValueError:
                print("Please enter a valid number.")
        
        # Calculate duration based on credits (rough estimate)
        duration_weeks = credits * 4  # 4 weeks per credit
        
        human_in_loop = input("Enable human-in-the-loop review? (y/n): ").lower().strip() == 'y'
        
        ollama_host = input("Ollama host (default: http://localhost:11434): ").strip()
        if not ollama_host:
            ollama_host = "http://localhost:11434"
        
        model = input("Model name (default: llama3.1): ").strip()
        if not model:
            model = "llama3.1"
        
        return MOOCConfig(
            topic=topic,
            credits=credits,
            duration_weeks=duration_weeks,
            human_in_loop=human_in_loop,
            ollama_host=ollama_host,
            base_model=model
        )

async def main():
    """Main function to run the MOOC generator"""
    
    # Check if Ollama is available
    test_client = OllamaClient()
    models = await test_client.list_models()
    
    if not models:
        print("Error: Cannot connect to Ollama. Please ensure Ollama is running.")
        print("Install Ollama from: https://ollama.ai")
        return
    
    print(f"Available models: {', '.join(models)}")
    
    # Get user configuration
    config = MOOCInterface.get_user_input()
    
    # Validate model exists
    if config.base_model not in models:
        print(f"Model {config.base_model} not found. Please pull it first:")
        print(f"ollama pull {config.base_model}")
        return
    
    # Generate MOOC
    generator = MOOCGenerator(config)
    
    try:
        result = await generator.generate_mooc()
        print(f"\n✅ MOOC generation completed!")
        print(f"Output directory: {result['output_directory']}")
        
    except Exception as e:
        logger.error(f"Error generating MOOC: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())