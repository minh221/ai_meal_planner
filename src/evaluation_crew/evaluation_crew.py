from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from crewai_tools import FileWriterTool
import os
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Union
from crewai.tasks import TaskOutput
from src.types.type_model import *

google_embedder={
		"provider": "google",
		"config": {
			"model": "models/text-embedding-004",
			"api_key": os.getenv("GEMINI_API_KEY"),
		}
	}


@CrewBase
class EvaluatorCrew:
    def __init__(self, knowledge_paths: Optional[List[str]] = None):
        self.knowledge_paths = knowledge_paths # e.g., ['/path/to/knowledge.md']

    llm_model = LLM(
			model="gemini/gemini-2.0-flash",
			temperature=0.7,
			api_key=os.getenv("GEMINI_API_KEY")
		)
	
    # llm_model = LLM(
	# 	model="openrouter/microsoft/phi-4-reasoning-plus:free",
	# 	base_url="https://openrouter.ai/api/v1",
	# 	api_key=os.getenv("OPENROUTER_API_KEY"),
	# 	temperature=0.7,
	# )
	
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def allergy_inspector(self) -> Agent:
        return Agent(
            config=self.agents_config['allergy_inspector'],
            llm=self.llm_model,
            verbose=True,
            embedder=google_embedder
        )
    

    @agent
    def health_condition_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['health_condition_analyst'],
            llm=self.llm_model,
            verbose=True,
            embedder=google_embedder
        )
      

    @agent
    def dietary_preference_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['dietary_preference_evaluator'],
            llm=self.llm_model,
            verbose=True,
            embedder=google_embedder
        )
    @agent
    def food_preference_analyst(self):
        return Agent(
            config=self.agents_config['food_preference_analyst'],
            llm=self.llm_model,
            verbose=True,
            embedder=google_embedder
        )

    @agent
    def nutrition_evaluator(self):
        return Agent(
            config=self.agents_config['nutrition_evaluator'],
            llm=self.llm_model,
            verbose=True,
            embedder=google_embedder
        )

    @agent
    def variety_analyst(self):
        return Agent(
            config=self.agents_config['variety_analyst'],
            llm=self.llm_model,
            verbose=True,
            embedder=google_embedder
        )

    # @agent
    # def evaluation_synthesizer(self):
    #     return Agent(
    #         config=self.agents_config['evaluation_synthesizer'],
    #         llm=self.llm_model,
    #         verbose=True,
    #         embedder=google_embedder
    #     )
    
    @task
    def allergy_inspector_task(self) -> Task:
        return Task(
            config=self.tasks_config['allergy_inspector_task'], 
            output_pydantic=Criteria
        )
    
    @task
    def health_condition_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['health_condition_analyst_task'], 
            output_pydantic=Criteria
        )
    
    @task
    def dietary_preference_evaluator_task(self) -> Task:
        return Task(
            config=self.tasks_config['dietary_preference_evaluator_task'], 
            output_pydantic=Criteria
        )
    
    @task
    def nutrition_evaluator_task(self) -> Task:
        return Task(
            config=self.tasks_config['nutrition_evaluator_task'], 
            output_pydantic=Criteria
        )
    
    @task
    def variety_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['variety_analyst_task'], 
            output_pydantic=Criteria
        )
    
    # @task
    # def evaluation_synthesizer_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['evaluation_synthesizer_task'], 
    #         output_pydantic=EvaluationOutput
    #     )
        
    @crew
    def crew(self) -> Crew:
        """A crew that evaluates meal plans based on user profiles."""
        if self.knowledge_paths is None:
            return Crew(
                agents=self.agents,
                tasks=self.tasks, 
                process=Process.sequential,
                verbose=True,
            )
        else: 
            return Crew(
                agents=self.agents,
                tasks=self.tasks, 
                process=Process.sequential,
                knowledge_sources=[CrewDoclingSource(file_paths=self.knowledge_paths)],
                verbose=True,
                embedder=google_embedder
            )
   
    