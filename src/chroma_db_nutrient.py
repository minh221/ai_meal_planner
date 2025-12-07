import os
import pandas as pd
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema.document import Document
from crewai import Agent, Task, Crew, Tool
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Load environment variables (store your OPENAI_API_KEY here)
load_dotenv()

class FoodNutritionRAG:
    def __init__(self, csv_path, persist_directory="./food_nutrition_db"):
        """
        Initialize the Food Nutrition RAG system
        
        Args:
            csv_path: Path to the CSV file containing food nutrition data
            persist_directory: Directory to store the Chroma database
        """
        self.csv_path = csv_path
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        self.vector_db = None
        
        # Check if the database already exists to avoid re-embedding
        if os.path.exists(persist_directory) and os.listdir(persist_directory):
            print("Loading existing Chroma database...")
            self.vector_db = Chroma(
                persist_directory=persist_directory,
                embedding_function=self.embeddings
            )
        else:
            print("Creating new Chroma database from CSV...")
            self._create_vector_db_from_csv()
    
    def _create_vector_db_from_csv(self):
        """Create and persist a Chroma database from the CSV file"""
        # Load the CSV data
        df = pd.read_csv(self.csv_path)
        
        # Convert DataFrame rows to documents for vectorization
        documents = []
        for idx, row in df.iterrows():
            # Convert row to string format for embedding
            content = " ".join([f"{col}: {val}" for col, val in row.items()])
            metadata = row.to_dict()  # Store all row data as metadata for retrieval
            doc = Document(page_content=content, metadata=metadata)
            documents.append(doc)
        
        # Optional: Split documents if they're very large
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
        split_documents = text_splitter.split_documents(documents)
        
        # Create and persist the vector database
        self.vector_db = Chroma.from_documents(
            documents=split_documents, 
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        self.vector_db.persist()
        print(f"Created and persisted Chroma DB with {len(split_documents)} documents")
    
    def search_food_database(self, query, num_results=5):
        """
        Search the food database using a natural language query
        
        Args:
            query: Natural language query about food or nutrition
            num_results: Number of results to return
            
        Returns:
            List of relevant food items with their nutritional data
        """
        if not self.vector_db:
            raise ValueError("Vector database not initialized")
            
        results = self.vector_db.similarity_search(query, k=num_results)
        return [doc.metadata for doc in results]
    
    def get_crewai_tool(self):
        """Create a CrewAI tool for the RAG system"""
        return Tool(
            name="Food Nutrition Database",
            description="Search for foods and their nutritional information using natural language queries",
            func=self.search_food_database
        )

# Example usage
if __name__ == "__main__":
    # Initialize the RAG system
    food_rag = FoodNutritionRAG(csv_path="food_nutrition_data.csv")
    
    # Test the search functionality
    results = food_rag.search_food_database("high protein low carb foods")
    for result in results:
        print(result)
    
    # Create a CrewAI agent with the RAG tool
    nutrition_tool = food_rag.get_crewai_tool()
    
    nutritionist = Agent(
        role="Nutritionist",
        goal="Create personalized meal plans based on nutritional requirements",
        backstory="You are an expert nutritionist who creates balanced meal plans",
        verbose=True,
        tools=[nutrition_tool]
    )
    
    meal_planning_task = Task(
        description="Create a meal plan with high protein, low carb options for an active adult",
        agent=nutritionist
    )
    
    crew = Crew(
        agents=[nutritionist],
        tasks=[meal_planning_task],
        verbose=2
    )
    
    result = crew.kickoff()
    print(result)