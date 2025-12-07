from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import os
from src.types.type_model import *
from langchain_huggingface import HuggingFaceEndpoint
import litellm
# litellm._turn_on_debug()

class GovRestrictedSearchTool(SerperDevTool):
    """
    Custom search tool that restricts all search queries to trusted government sources.
    Specifically: nih.gov, cdc.gov, usda.gov, and other .gov domains.
    """

    def run(self, query: str, **kwargs) -> str:
        # show results only from trusted websites 
        restricted_query = f"{query} site:nih.gov OR site:cdc.gov OR site:usda.gov OR site:.gov"
        print(f"[GovRestrictedSearchTool] Query sent: {restricted_query}")
        return super().run(restricted_query, **kwargs)

@CrewBase
class SearchCrew():
	"""A crew that helps you with nutrition research and report generation."""

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
	def nutrition_advisor(self) -> Agent:
		return Agent(
			config=self.agents_config['nutrition_advisor'],
			llm=self.llm_model,
			tools=[GovRestrictedSearchTool(), ScrapeWebsiteTool()],
			verbose=True
		)

	@agent
	def nutrition_report_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['nutrition_report_creator'],
			llm=self.llm_model,
			verbose=True
		)

	@task
	def nutrition_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['nutrition_research_task'],
		)

	@task
	def nutrition_reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['nutrition_reporting_task']
		)

	@crew
	def crew(self) -> Crew:
		"""A crew that helps you with nutrition research and report generation."""
		return Crew(
			agents=self.agents,
			tasks=self.tasks, 
			process=Process.sequential,
			verbose=True,
		)