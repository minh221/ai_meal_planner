from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from crewai import LLM
import torch
import os

# --- Pydantic Model ---
class LoginRequest(BaseModel):
    user_id: str
    password: str
    
class UserProfile(BaseModel):
    user_id: int
    number_of_days: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    health_conditions: str  # comma-separated string
    dietary_preferences: str
    allergies: str
    nutritional_goals: str
    food_preferences: str

class RecipeBase(BaseModel):
    id: int
    title: str
    type: str
    diet: str
    ingredients: str
    instructions: str
    calories: float
    protein: float
    fat: float
    carbs: float

class FavoriteBase(BaseModel):
    user_id: int
    recipe_id: int

class FavoriteOut(BaseModel):
    user_id: int
    recipe_id: int
    added_at: str


class MealPlanRequest(BaseModel):
    user_id: str
    meal_plan: str


# Define the Pydantic model for the meal planning output
class FoodItem(BaseModel):
    name: str = Field(..., description="Name of the food item")
    portion_size: str = Field(..., description="Portion size of the food item")
    calories: float = Field(..., description="Calories in the food item")
    protein: float = Field(..., description="Protein content in grams")
    fat: float = Field(..., description="Fat content in grams")
    carbs: float = Field(..., description="Carbohydrate content in grams")
    preparation: Optional[str] = Field(None, description="Basic preparation instructions")



class Meal(BaseModel):
    name: str = Field(..., description="Name of the meal (e.g., 'Breakfast', 'Lunch', 'Dinner', 'Snack')")
    foods: List[FoodItem] = Field(..., description="List of foods included in this meal")

class DailyMealPlan(BaseModel):
    day: int = Field(..., description="Day number in the meal plan")
    meals: List[Meal] = Field(..., description="List of meals for this day")
    daily_advice: Optional[str] = Field(None, description="Specific advice for this day")

class MealPlanOutput(BaseModel):
    meal_plan: List[DailyMealPlan] = Field(..., description="Daily meal plans for the requested duration")
    health_condition_considerations: Dict[str, str] = Field(
        ..., 
        description="How the meal plan addresses each health condition"
    )
    dietary_accommodations: Dict[str, str] = Field(
        ..., 
        description="How dietary preferences and allergies were accommodated"
    )
    general_advice: str = Field(..., description="General advice for following the meal plan")

class Criteria(BaseModel):
    score: int = Field(..., ge=0, le=10, description="Score for the criteria")
    justification: str = Field(..., description="Justification for the score")
    

class EvaluationOutput(BaseModel):
    allergies_detected: bool = Field(..., description="True if the meal plan contains ingredients the user is allergic to")
    health_condition_compatibility: int = Field(..., ge=1, le=10, description="Score (1-10) indicating compatibility with user's health conditions")
    diet_preference_adherence: int = Field(..., ge=1, le=10, description="Score (1-10) indicating adherence to user's dietary preferences (e.g., keto, vegan)")
    food_preferences_relevant: int = Field(..., ge=1, le=10, description="Score (1-10) based on inclusion of foods the user likes or avoidance of disliked items")
    nutritional_balance: int = Field(..., ge=1, le=10, description="Score (1-10) for the overall nutritional quality and balance")
    variety: int = Field(..., ge=1, le=10, description="Score (1-10) based on variety of meals/ingredients included")
    justification: str = Field(..., description="Combine justification for all the scores given")