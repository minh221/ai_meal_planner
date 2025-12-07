from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import CSVSearchTool
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
import os

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from crewai import Task
from crewai.tasks import TaskOutput
from src.types.type_model import *

tool = CSVSearchTool(
	csv_path="knowledge/food_data.csv",
	search_column="food",
	output_columns=['food','calories','protein','fat','carbohydrates'],
	tool_name="FoodNutrientSearchTool",
	description="A tool to search for nutrient information per 100g of food."
)

google_embedder={
		"provider": "google",
		"config": {
			"model": "models/text-embedding-004",
			"api_key": os.getenv("GEMINI_API_KEY"),
		}
	}

@CrewBase
class MealPlanCrew():
	"""A crew that give you tailored meals for your health can preferences."""
	def __init__(self, knowledge_paths: Optional[List[str]] = None):
		self.knowledge_paths = knowledge_paths # e.g., ['/path/to/knowledge.md']

	# llm_model = LLM(
	# 		model="gemini/gemini-2.0-flash",
	# 		temperature=0.7,
	# 		api_key=os.getenv("GEMINI_API_KEY")
	# 	)
	
	llm_model = LLM(
		model="openrouter/microsoft/phi-4-reasoning-plus:free",
		base_url="https://openrouter.ai/api/v1",
		api_key=os.getenv("OPENROUTER_API_KEY"),
		temperature=0.7,
	)
	
	agents_config = "config/agents.yaml"

	tasks_config = "config/tasks.yaml"

	@agent
	def meal_planner(self) -> Agent:
		return Agent(
			config=self.agents_config['meal_planner'],
			llm=self.llm_model,
			tools=[tool],
			verbose=True,
			embedder= google_embedder
		)

	@task
	def meal_planning_task(self) -> Task:
		return Task(
			config=self.tasks_config['meal_planning_task'], output_pydantic=MealPlanOutput
		)


	@crew
	def crew(self) -> Crew:
		"""A crew that give you tailored meals for your health can preferences."""
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
			embedder= google_embedder
		)