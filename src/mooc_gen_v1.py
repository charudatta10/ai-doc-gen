#!/usr/bin/env python3
"""
MOOC Generator System with Ollama Integration
Generates complete MOOC courses with AI agents for content creation
"""

import json
import os
import asyncio
import aiohttp
import re
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
        spanning {duration_weeks} weeks. 

        Please format your response as a JSON structure with the following format:
        {{
            "course_title": "Complete course title",
            "description": "Detailed course description (200-300 words)",
            "learning_outcomes": [
                "Specific, measurable learning outcome 1",
                "Specific, measurable learning outcome 2",
                "Specific, measurable learning outcome 3",
                "Specific, measurable learning outcome 4",
                "Specific, measurable learning outcome 5"
            ],
            "modules": [
                {{
                    "week": 1,
                    "title": "Specific module title for week 1",
                    "description": "Detailed description of what will be covered",
                    "learning_objectives": [
                        "Specific objective 1 for this module",
                        "Specific objective 2 for this module"
                    ]
                }}
                // ... continue for all {duration_weeks} weeks
            ],
            "assessment_structure": {{
                "assignments": 0.4,
                "midterm_exam": 0.2,
                "final_project": 0.25,
                "participation": 0.15
            }},
            "references": [
                "Author, A. (Year). Title of Book/Article. Publisher.",
                "Author, B. (Year). Another Reference. Journal Name.",
                "Relevant online resource or textbook",
                "Additional academic reference"
            ]
        }}

        Make sure all content is specific to "{topic}" and appropriate for a {credits}-credit university course.
        """
        
        context = f"""
        You are creating a syllabus for a {credits}-credit university course on {topic}.
        Focus on creating academically rigorous content suitable for higher education.
        Ensure proper progression of difficulty and comprehensive coverage of the topic.
        Make learning outcomes specific and measurable using action verbs like "analyze", "evaluate", "create", "apply".
        Each module should build upon previous knowledge and have clear, specific titles and descriptions.
        """
        
        response = await self.generate_content(prompt, context)
        return await self._parse_syllabus_response(response, topic, credits, duration_weeks)
    
    async def _parse_syllabus_response(self, response: str, topic: str, credits: int, duration_weeks: int) -> Syllabus:
        """Parse LLM response into Syllabus object"""
        try:
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                try:
                    data = json.loads(json_str)
                    
                    # Create modules from parsed data
                    modules = []
                    for module_data in data.get('modules', []):
                        module = Module(
                            id=f"module_{module_data.get('week', 1)}",
                            title=module_data.get('title', f"Week {module_data.get('week', 1)} Module"),
                            description=module_data.get('description', 'Module description'),
                            week=module_data.get('week', 1),
                            learning_objectives=module_data.get('learning_objectives', []),
                            content_types=['video', 'notes', 'quiz', 'assignment']
                        )
                        modules.append(module)
                    
                    return Syllabus(
                        course_title=data.get('course_title', f"{topic} - {credits} Credit Course"),
                        credits=credits,
                        duration_weeks=duration_weeks,
                        description=data.get('description', 'Course description'),
                        learning_outcomes=data.get('learning_outcomes', []),
                        modules=modules,
                        assessment_structure=data.get('assessment_structure', {}),
                        references=data.get('references', [])
                    )
                
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON, using fallback parsing")
            
            # Fallback: Try to parse structured text
            return await self._parse_text_syllabus(response, topic, credits, duration_weeks)
            
        except Exception as e:
            logger.error(f"Error parsing syllabus: {e}")
            # Return a basic fallback syllabus
            return await self._create_fallback_syllabus(topic, credits, duration_weeks)
    
    async def _parse_text_syllabus(self, response: str, topic: str, credits: int, duration_weeks: int) -> Syllabus:
        """Parse text-based syllabus response"""
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        # Extract course title
        course_title = f"{topic} - {credits} Credit Course"
        for line in lines:
            if 'course title' in line.lower() or 'title:' in line.lower():
                title_parts = line.split(':', 1)
                if len(title_parts) > 1:
                    course_title = title_parts[1].strip()
                break
        
        # Extract description
        description = f"A comprehensive {credits}-credit course covering {topic}"
        
        # Extract learning outcomes
        learning_outcomes = []
        in_outcomes = False
        for line in lines:
            if 'learning outcome' in line.lower() or 'course objective' in line.lower():
                in_outcomes = True
                continue
            if in_outcomes and line.startswith(('-', '•', '1.', '2.', '3.', '4.', '5.')):
                outcome = re.sub(r'^[-•\d\.\s]+', '', line).strip()
                if outcome:
                    learning_outcomes.append(outcome)
            elif in_outcomes and not line.startswith(('-', '•')) and 'module' in line.lower():
                break
        
        # Create meaningful modules
        modules = await self._create_topic_modules(topic, duration_weeks)
        
        # Default assessment structure
        assessment_structure = {
            "assignments": 0.4,
            "midterm_exam": 0.2,
            "final_project": 0.25,
            "participation": 0.15
        }
        
        # Basic references
        references = [
            f"Primary textbook on {topic}",
            f"Recent journal articles in {topic}",
            f"Online resources and case studies",
            f"Professional publications in {topic}"
        ]
        
        return Syllabus(
            course_title=course_title,
            credits=credits,
            duration_weeks=duration_weeks,
            description=description,
            learning_outcomes=learning_outcomes if learning_outcomes else await self._generate_learning_outcomes(topic),
            modules=modules,
            assessment_structure=assessment_structure,
            references=references
        )
    
    async def _create_topic_modules(self, topic: str, duration_weeks: int) -> List[Module]:
        """Create topic-specific modules"""
        # Generate module structure based on topic
        prompt = f"""
        Create {duration_weeks} weekly module titles for a course on "{topic}".
        Each module should build upon the previous and cover different aspects of {topic}.
        
        Format as:
        Week 1: [Specific Module Title]
        Week 2: [Specific Module Title]
        ...
        
        Make titles specific and progressive, not generic.
        """
        
        response = await self.generate_content(prompt, f"Focus on {topic} curriculum design")
        
        modules = []
        lines = response.split('\n')
        
        for i in range(duration_weeks):
            week_num = i + 1
            
            # Try to extract from response
            module_title = f"Module {week_num}"
            for line in lines:
                if f"week {week_num}" in line.lower():
                    parts = line.split(':', 1)
                    if len(parts) > 1:
                        module_title = parts[1].strip()
                    break
            
            # Generate learning objectives for this module
            objectives_prompt = f"List 2-3 specific learning objectives for a module titled '{module_title}' in a {topic} course."
            objectives_response = await self.generate_content(objectives_prompt)
            
            objectives = []
            for obj_line in objectives_response.split('\n'):
                obj_line = obj_line.strip()
                if obj_line and (obj_line.startswith(('-', '•', '1.', '2.', '3.')) or len(objectives) == 0):
                    clean_obj = re.sub(r'^[-•\d\.\s]+', '', obj_line).strip()
                    if clean_obj and len(clean_obj) > 10:
                        objectives.append(clean_obj)
                        if len(objectives) >= 3:
                            break
            
            if not objectives:
                objectives = [f"Understand key concepts in {module_title.lower()}", 
                            f"Apply {topic} principles to practical scenarios"]
            
            module = Module(
                id=f"module_{week_num}",
                title=module_title,
                description=f"This module covers {module_title.lower()} as part of the {topic} curriculum.",
                week=week_num,
                learning_objectives=objectives,
                content_types=['video', 'notes', 'quiz', 'assignment']
            )
            modules.append(module)
        
        return modules
    
    async def _generate_learning_outcomes(self, topic: str) -> List[str]:
        """Generate meaningful learning outcomes for the topic"""
        prompt = f"""
        Create 5 specific, measurable learning outcomes for a university course on "{topic}".
        Use action verbs like analyze, evaluate, create, apply, synthesize.
        Each outcome should be specific to {topic} and measurable.
        
        Format as a simple list, one per line.
        """
        
        response = await self.generate_content(prompt)
        outcomes = []
        
        for line in response.split('\n'):
            line = line.strip()
            if line and (line.startswith(('-', '•', '1.', '2.', '3.', '4.', '5.')) or len(outcomes) == 0):
                clean_outcome = re.sub(r'^[-•\d\.\s]+', '', line).strip()
                if clean_outcome and len(clean_outcome) > 15:
                    outcomes.append(clean_outcome)
                    if len(outcomes) >= 5:
                        break
        
        if not outcomes:
            outcomes = [
                f"Analyze fundamental concepts and principles in {topic}",
                f"Evaluate different approaches and methodologies in {topic}",
                f"Apply {topic} knowledge to solve real-world problems",
                f"Create original solutions using {topic} frameworks",
                f"Synthesize information from multiple sources in {topic}"
            ]
        
        return outcomes
    
    async def _create_fallback_syllabus(self, topic: str, credits: int, duration_weeks: int) -> Syllabus:
        """Create a basic syllabus when parsing fails"""
        logger.info("Creating fallback syllabus")
        
        modules = []
        for week in range(1, duration_weeks + 1):
            module = Module(
                id=f"module_{week}",
                title=f"{topic} Fundamentals - Week {week}",
                description=f"Week {week} covers essential concepts in {topic}",
                week=week,
                learning_objectives=[
                    f"Understand key concepts from week {week}",
                    f"Apply {topic} principles in practical contexts"
                ],
                content_types=['video', 'notes', 'quiz', 'assignment']
            )
            modules.append(module)
        
        return Syllabus(
            course_title=f"{topic} - {credits} Credit Course",
            credits=credits,
            duration_weeks=duration_weeks,
            description=f"A comprehensive {credits}-credit course covering fundamental and advanced concepts in {topic}.",
            learning_outcomes=[
                f"Analyze core principles and concepts in {topic}",
                f"Evaluate different methodologies and approaches in {topic}",
                f"Apply {topic} knowledge to solve practical problems",
                f"Create innovative solutions using {topic} frameworks",
                f"Synthesize complex information from multiple {topic} sources"
            ],
            assessment_structure={
                "assignments": 0.4,
                "midterm_exam": 0.2,
                "final_project": 0.25,
                "participation": 0.15
            },
            references=[
                f"Comprehensive textbook on {topic}",
                f"Current research publications in {topic}",
                f"Industry reports and case studies",
                f"Online learning resources and databases"
            ]
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
        """Human-in-the-loop syllabus review with editing capabilities"""
        while True:
            print("\n" + "="*60)
            print("SYLLABUS REVIEW")
            print("="*60)
            print(f"Course: {syllabus.course_title}")
            print(f"Credits: {syllabus.credits}")
            print(f"Duration: {syllabus.duration_weeks} weeks")
            print(f"Description: {syllabus.description}")
            
            print(f"\nLearning Outcomes ({len(syllabus.learning_outcomes)}):")
            for i, outcome in enumerate(syllabus.learning_outcomes, 1):
                print(f"  {i}. {outcome}")
            
            print(f"\nModules ({len(syllabus.modules)}):")
            for module in syllabus.modules:
                print(f"  Week {module.week}: {module.title}")
                print(f"    - {module.description}")
            
            print(f"\nAssessment Structure:")
            for component, weight in syllabus.assessment_structure.items():
                print(f"  - {component.title()}: {weight*100:.0f}%")
            
            print(f"\nReferences ({len(syllabus.references)}):")
            for i, ref in enumerate(syllabus.references, 1):
                print(f"  {i}. {ref}")
            
            print("\nOptions:")
            print("1. Approve syllabus")
            print("2. Edit course title")
            print("3. Edit description")
            print("4. Edit learning outcomes")
            print("5. Edit module titles")
            print("6. Edit assessment structure")
            print("7. Regenerate entire syllabus")
            print("8. Add/edit references")
            
            choice = input("\nSelect option (1-8): ").strip()
            
            if choice == '1':
                print("✅ Syllabus approved!")
                return syllabus
            
            elif choice == '2':
                new_title = input(f"Current title: {syllabus.course_title}\nNew title: ").strip()
                if new_title:
                    syllabus.course_title = new_title
            
            elif choice == '3':
                print(f"Current description: {syllabus.description}")
                new_desc = input("New description (press Enter for current): ").strip()
                if new_desc:
                    syllabus.description = new_desc
            
            elif choice == '4':
                syllabus = await self._edit_learning_outcomes(syllabus)
            
            elif choice == '5':
                syllabus = await self._edit_modules(syllabus)
            
            elif choice == '6':
                syllabus = self._edit_assessment_structure(syllabus)
            
            elif choice == '7':
                print("Regenerating syllabus...")
                confirm = input("This will replace the entire syllabus. Continue? (y/n): ").lower()
                if confirm == 'y':
                    new_syllabus = await self.create_syllabus(
                        syllabus.course_title.split(' - ')[0], 
                        syllabus.credits, 
                        syllabus.duration_weeks
                    )
                    return await self._review_syllabus(new_syllabus)
            
            elif choice == '8':
                syllabus = self._edit_references(syllabus)
            
            else:
                print("Invalid option. Please try again.")
    
    async def _edit_learning_outcomes(self, syllabus: Syllabus) -> Syllabus:
        """Edit learning outcomes"""
        print("\nCurrent Learning Outcomes:")
        for i, outcome in enumerate(syllabus.learning_outcomes, 1):
            print(f"{i}. {outcome}")
        
        print("\nOptions:")
        print("1. Add new outcome")
        print("2. Edit existing outcome")
        print("3. Delete outcome")
        print("4. Regenerate all outcomes")
        print("5. Return to main menu")
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            new_outcome = input("Enter new learning outcome: ").strip()
            if new_outcome:
                syllabus.learning_outcomes.append(new_outcome)
        
        elif choice == '2':
            try:
                index = int(input("Enter outcome number to edit: ")) - 1
                if 0 <= index < len(syllabus.learning_outcomes):
                    current = syllabus.learning_outcomes[index]
                    new_outcome = input(f"Current: {current}\nNew outcome: ").strip()
                    if new_outcome:
                        syllabus.learning_outcomes[index] = new_outcome
                else:
                    print("Invalid outcome number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '3':
            try:
                index = int(input("Enter outcome number to delete: ")) - 1
                if 0 <= index < len(syllabus.learning_outcomes):
                    removed = syllabus.learning_outcomes.pop(index)
                    print(f"Removed: {removed}")
                else:
                    print("Invalid outcome number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '4':
            topic = syllabus.course_title.split(' - ')[0]
            new_outcomes = await self._generate_learning_outcomes(topic)
            syllabus.learning_outcomes = new_outcomes
            print("Learning outcomes regenerated.")
        
        return syllabus
    
    async def _edit_modules(self, syllabus: Syllabus) -> Syllabus:
        """Edit module titles and descriptions"""
        print("\nCurrent Modules:")
        for i, module in enumerate(syllabus.modules, 1):
            print(f"{i}. Week {module.week}: {module.title}")
        
        try:
            index = int(input("Enter module number to edit (0 to return): ")) - 1
            if index == -1:
                return syllabus
            
            if 0 <= index < len(syllabus.modules):
                module = syllabus.modules[index]
                print(f"Current title: {module.title}")
                print(f"Current description: {module.description}")
                
                new_title = input("New title (press Enter to keep current): ").strip()
                if new_title:
                    module.title = new_title
                
                new_desc = input("New description (press Enter to keep current): ").strip()
                if new_desc:
                    module.description = new_desc
                
                print("Module updated!")
            else:
                print("Invalid module number.")
        except ValueError:
            print("Please enter a valid number.")
        
        return syllabus
    
    def _edit_assessment_structure(self, syllabus: Syllabus) -> Syllabus:
        """Edit assessment structure"""
        print("\nCurrent Assessment Structure:")
        total_weight = 0
        for component, weight in syllabus.assessment_structure.items():
            print(f"  {component.title()}: {weight*100:.0f}%")
            total_weight += weight
        
        print(f"Total: {total_weight*100:.0f}%")
        
        if abs(total_weight - 1.0) > 0.01:
            print("⚠️  Warning: Weights don't sum to 100%")
        
        component = input("Enter component name to edit: ").strip().lower()
        if component in syllabus.assessment_structure:
            try:
                new_weight = float(input(f"Enter new weight for {component} (as decimal, e.g., 0.25 for 25%): "))
                if 0 <= new_weight <= 1:
                    syllabus.assessment_structure[component] = new_weight
                    print(f"Updated {component} to {new_weight*100:.0f}%")
                else:
                    print("Weight must be between 0 and 1.")
            except ValueError:
                print("Please enter a valid decimal number.")
        else:
            print(f"Component '{component}' not found.")
            add_new = input("Add as new component? (y/n): ").lower()
            if add_new == 'y':
                try:
                    weight = float(input("Enter weight (as decimal): "))
                    if 0 <= weight <= 1:
                        syllabus.assessment_structure[component] = weight
                        print(f"Added {component} with {weight*100:.0f}%")
                    else:
                        print("Weight must be between 0 and 1.")
                except ValueError:
                    print("Please enter a valid decimal number.")
        
        return syllabus
    
    def _edit_references(self, syllabus: Syllabus) -> Syllabus:
        """Edit references"""
        print("\nCurrent References:")
        for i, ref in enumerate(syllabus.references, 1):
            print(f"{i}. {ref}")
        
        print("\nOptions:")
        print("1. Add reference")
        print("2. Edit reference")
        print("3. Delete reference")
        print("4. Return to main menu")
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            new_ref = input("Enter new reference: ").strip()
            if new_ref:
                syllabus.references.append(new_ref)
        
        elif choice == '2':
            try:
                index = int(input("Enter reference number to edit: ")) - 1
                if 0 <= index < len(syllabus.references):
                    current = syllabus.references[index]
                    new_ref = input(f"Current: {current}\nNew reference: ").strip()
                    if new_ref:
                        syllabus.references[index] = new_ref
                else:
                    print("Invalid reference number.")
            except ValueError:
                print("Please enter a valid number.")
        
        elif choice == '3':
            try:
                index = int(input("Enter reference number to delete: ")) - 1
                if 0 <= index < len(syllabus.references):
                    removed = syllabus.references.pop(index)
                    print(f"Removed: {removed}")
                else:
                    print("Invalid reference number.")
            except ValueError:
                print("Please enter a valid number.")
        
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