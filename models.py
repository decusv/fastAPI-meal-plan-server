"""
models.py

This module contains Pydantic models for handling meal plans.

"""
from typing import List, Optional
from pydantic import BaseModel, Field


class NutritionalInformation(BaseModel):
    """
    Pydantic model for nutritional information of a recipe.

    Attributes:
        calories (float): The calorie content.
        protein (float): The protein content.
        fiber (float): The fiber content.
    """
    calories: float
    protein: float
    fiber: float

class Recipe(BaseModel):
    """
    Pydantic model for a recipe.

    Attributes:
        name (str): The name of the recipe.
        description (str): The description of the recipe.
        steps (List[str]): The list of steps to prepare the recipe.
        tags (List[str]): List of tags for categorizing the recipe.
        nutritional_info (Optional[NutritionalInformation]): Optional nutritional information for the recipe.
    """
    name: str
    description: str
    steps: List[str]
    tags: List[str] = []
    nutritional_info: Optional[NutritionalInformation] = None

class Meal(BaseModel):
    """
    Pydantic model for a meal.

    Attributes:
        recipe (Recipe): The recipe associated with the meal.
    """
    recipe: Recipe

class CreateMealPlan(BaseModel):
    """
    Pydantic model for creating a meal plan.

    Attributes:
        name (str): The name of the meal plan.
        description (str): The description of the meal plan.
        meals (List[Meal]): The list of meals in the meal plan.
    """
    name: str
    description: str
    meals: List[Meal]

class MealPlanRequest(BaseModel):
    """
    Pydantic model for a meal plan request.

    Attributes:
        meal_tags (List[str]): List of meal tags to be used in generating the query.
    """
    meal_tags: List[str]

class MealPlan(BaseModel):
    """
    Pydantic model for a meal plan.

    Attributes:
        id (str): 7-letter alphanumeric identifier.
        name (str): The name of the meal plan.
        description (str): The description of the meal plan.
        meals (List[Meal]): The list of meals in the meal plan.
    """
    id: str = Field(min_length=7, max_length=7, pattern="^[a-zA-Z0-9]+$")
    name: str
    description: str
    meals: List[Meal]
