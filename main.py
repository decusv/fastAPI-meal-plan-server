"""
main.py

This file contains the main FastAPI application for managing meal plans. 
Includes endpoints for generating, reading, updating, and deleting meal plans.
 The application interacts with ChatGPT to generate meal plans based on specified meal tags.

Usage:
1. Start the FastAPI server using the command: `python -m uvicorn main:app --reload`.
2. Access the API documentation at `http://localhost:8000/docs` to explore and test the available endpoints.

Note:
- Ensure that the ChatGPT API key is configured in the 'config.py' file for generating meal plans.
- The application uses an in-memory database (`fake_db`) to store meal plans during runtime.
"""
import json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from models import MealPlanRequest, MealPlan
from functions import generate_identifier, generate_meal_plan
from google.cloud import firestore
from google.cloud.firestore_v1 import Client
import os

key_file_path = r"hazel-charter-408317-17272dc7fc29.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_file_path

# Create a FastAPI instance
app = FastAPI()

# In-memory database to store meal plans
fake_db = []

# Firestore configuration
project_id = "hazel-charter-408317"
database_id = "meal-plan-db" 
collection_name = "meal-plans"

# Initialize Firestore client
try:
    firestore_client = firestore.Client()
    print("Firestore client initialized successfully!")
except Exception as e:
    print(f"Error initializing Firestore client: {e}")

def get_firestore_client():
    return firestore.Client(project=project_id, database=database_id)

# Function to create a meal plan in Firestore
def create_meal_plan_firestore(meal_plan_id: str, meal_plan_data: dict, firestore_client: Client):
    meal_plan_ref = firestore_client.collection(collection_name).document(meal_plan_id)
    meal_plan_ref.set(meal_plan_data)

# Function to read a meal plan from Firestore
def read_meal_plan_firestore(meal_plan_id: str, firestore_client: Client):
    meal_plan_ref = firestore_client.collection(collection_name).document(meal_plan_id)
    meal_plan_data = meal_plan_ref.get().to_dict()
    return meal_plan_data

# Function to update a meal plan in Firestore
def update_meal_plan_firestore(meal_plan_id: str, meal_plan_data: dict, firestore_client: Client):
    meal_plan_ref = firestore_client.collection(collection_name).document(meal_plan_id)
    meal_plan_ref.update(meal_plan_data)

# Function to delete a meal plan from Firestore
def delete_meal_plan_firestore(meal_plan_id: str, firestore_client: Client):
    meal_plan_ref = firestore_client.collection(collection_name).document(meal_plan_id)
    meal_plan_data = meal_plan_ref.get().to_dict()
    meal_plan_ref.delete()
    return meal_plan_data



@app.post("/meal-plans/generate")
def create_meal_plan(meal_plan_request: MealPlanRequest, firestore_client: Client = Depends(get_firestore_client)):
    """
    Create a new meal plan using ChatGPT based on provided meal tags.

    Parameters:
    - meal_plan_request (MealPlanRequest): The request containing meal tags.

    Returns:
    - JSONResponse: A JSON response containing the generated meal plan and its unique identifier.
    """
    meal_plan_tags = meal_plan_request.meal_tags
    meal_plan_id = generate_identifier()
    generated_meal_plan_result = generate_meal_plan(meal_plan_tags)
    formatted_response = {
        "id": meal_plan_id,
        "result": json.loads(generated_meal_plan_result['generated_meal_plan'])
    }

    # Save the meal plan to Firestore
    create_meal_plan_firestore(meal_plan_id, formatted_response, firestore_client)

    return JSONResponse(content=formatted_response)


@app.get("/debug/get-database")
def retrieve_current_database_view():
    """
    Debug endpoint to retrieve the contents of the in-memory meal plans database (fake_db).

    Returns:
        List[MealPlan]: A list containing the meal plans stored in the in-memory database.
    """
    return fake_db

# Endpoint to read a meal plan by its identifier
@app.get("/meal-plans/{meal_plan_id}")
def read_meal_plan(meal_plan_id: str, firestore_client: Client = Depends(get_firestore_client)):
    """
    Retrieve a meal plan by its unique identifier.

    Parameters:
    - `meal_plan_id`: The 7-character alphanumeric identifier for the meal plan.

    Returns:
    - If found, returns the details of the meal plan.
    - If not found, raises an HTTPException with a 404 status code and a detailed error message.
    """
    meal_plan_data = read_meal_plan_firestore(meal_plan_id, firestore_client)
    if meal_plan_data:
        return meal_plan_data
    raise HTTPException(status_code=404, detail="Meal plan not found")

# Endpoint to update an existing meal plan
@app.put("/meal-plans/{meal_plan_id}")
def update_meal_plan(meal_plan_id: str, meal_plan: MealPlan, firestore_client: Client = Depends(get_firestore_client)):
    """
    Update an existing meal plan by providing a new set of details.

    Parameters:
    - `meal_plan_id`: The 7-character alphanumeric identifier for the meal plan.
    - `meal_plan`: The updated details of the meal plan.

    Returns:
    - If the meal plan is found and updated successfully, returns a success message.
    - If the meal plan is not found, raises an HTTPException with a 404 status code.
    """

    meal_plan_data = meal_plan.model_dump(exclude_unset=True)
    update_meal_plan_firestore(meal_plan_id, meal_plan_data, firestore_client)
    return {"meal_plan_id": meal_plan_id, "meal_plan_name": meal_plan.name,
            "message": "Meal plan updated successfully"}

# Endpoint to delete an existing meal plan
@app.delete("/meal-plans/{meal_plan_id}")
def delete_meal_plan(meal_plan_id: str, firestore_client: Client = Depends(get_firestore_client)):
    """
    Delete an existing meal plan by its unique identifier.

    Parameters:
    - `meal_plan_id`: The 7-character alphanumeric identifier for the meal plan.

    Returns:
    - If the meal plan is found and deleted successfully, returns a success message.
    - If the meal plan is not found, raises an HTTPException with a 404 status code.
    """
    meal_plan_data = delete_meal_plan_firestore(meal_plan_id, firestore_client)
    if meal_plan_data:
        return {"meal_plan_id": meal_plan_id, "meal_plan_name": meal_plan_data.get("name"),
                "message": "Meal plan deleted successfully"}
    raise HTTPException(status_code=404, detail="Meal plan not found")
