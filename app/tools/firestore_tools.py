"""Firestore tools for reading and saving recipes to Cloud Firestore."""

import json
import os
import re
import uuid
import requests
from google import genai
from google.cloud import firestore, storage
from google.genai import types
from google.adk.tools import ToolContext

# CRITICAL: Hardcode GCP Project ID and Bucket Name as strings.
# On Agent Platform, google.auth.default() returns project number which breaks Firestore & GCS.
PROJECT_ID = "qwiklabs-gcp-03-abe3a9744f22"
BUCKET_NAME = "sous-chef-recipes-qwiklabs-gcp-03-abe3a9744f22"


def _get_db() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)


def search_recipes(
    query: str = "",
    category: str = "",
    is_gluten_free: bool = None,
    max_cook_time_mins: int = None,
) -> str:
    """Search for recipes in the Firestore database based on category, dietary restrictions, or cook time.

    Args:
        query: Optional search keyword to filter by title or ingredient (e.g. 'chicken', 'cilantro').
        category: Optional recipe category (e.g. 'Mexican', 'Italian', 'Asian').
        is_gluten_free: Optional boolean flag to filter for gluten-free recipes.
        max_cook_time_mins: Optional maximum total cook time in minutes.

    Returns:
        A JSON string containing matching recipes found in the database.
    """
    db = _get_db()
    recipes_ref = db.collection("recipes")

    docs = recipes_ref.stream()
    matching_recipes = []

    for doc in docs:
        data = doc.to_dict()
        doc_id = doc.id
        data["id"] = doc_id

        # Category filter
        if category and data.get("category", "").lower() != category.lower():
            continue

        # Gluten-free filter
        if is_gluten_free is not None and data.get("is_gluten_free") != is_gluten_free:
            continue

        # Max cook time filter
        if max_cook_time_mins is not None and data.get("cook_time_mins", 0) > max_cook_time_mins:
            continue

        # Text query filter across title and ingredients
        if query:
            q_lower = query.lower()
            title_match = q_lower in data.get("title", "").lower()
            ingredient_match = any(q_lower in ing.lower() for ing in data.get("ingredients", []))
            if not (title_match or ingredient_match):
                continue

        matching_recipes.append(data)

    if not matching_recipes:
        return "No recipes found matching the specified criteria."

    return json.dumps(matching_recipes, indent=2)


def get_recipe(title_or_id: str) -> str:
    """Retrieve details for a specific recipe by its title or ID from Firestore.

    Args:
        title_or_id: The exact or partial title or document ID of the recipe.

    Returns:
        A JSON string with the complete recipe details, including ingredients and cooking instructions.
    """
    db = _get_db()
    recipes_ref = db.collection("recipes")

    doc_id = title_or_id.lower().replace(" ", "-")
    doc = recipes_ref.document(doc_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return json.dumps(data, indent=2)

    # Search by title match if ID didn't hit
    for d in recipes_ref.stream():
        data = d.to_dict()
        if title_or_id.lower() in data.get("title", "").lower():
            data["id"] = d.id
            return json.dumps(data, indent=2)

    return f"Recipe '{title_or_id}' not found in the database."


def add_recipe(
    title: str,
    category: str,
    prep_time_mins: int,
    cook_time_mins: int,
    is_gluten_free: bool,
    is_dairy_free: bool,
    ingredients: list[str],
    instructions: list[str],
) -> str:
    """Add a new recipe to the Cloud Firestore recipe collection.

    Args:
        title: The name of the recipe (e.g. 'Grilled Cilantro Lime Chicken').
        category: Cuisine or dish category (e.g. 'Mexican', 'Italian', 'Asian', 'American').
        prep_time_mins: Preparation time in minutes.
        cook_time_mins: Cooking time in minutes.
        is_gluten_free: True if the recipe is gluten-free, False otherwise.
        is_dairy_free: True if the recipe is dairy-free, False otherwise.
        ingredients: List of ingredients with quantities (e.g. ['1 lb chicken thighs', '2 limes']).
        instructions: Step-by-step cooking instructions.

    Returns:
        A confirmation message with the generated recipe document ID.
    """
    db = _get_db()
    recipes_ref = db.collection("recipes")

    doc_id = title.lower().replace(" ", "-")
    recipe_data = {
        "title": title,
        "category": category,
        "prep_time_mins": prep_time_mins,
        "cook_time_mins": cook_time_mins,
        "is_gluten_free": is_gluten_free,
        "is_dairy_free": is_dairy_free,
        "ingredients": ingredients,
        "instructions": instructions,
    }

    recipes_ref.document(doc_id).set(recipe_data)
    return f"Successfully added recipe '{title}' to Firestore with ID: '{doc_id}'."


def scale_recipe_yield(
    title_or_id: str,
    target_servings: int,
    base_servings: int = 4,
) -> str:
    """Scale the ingredient quantities of a recipe to match target servings.

    Args:
        title_or_id: The title or document ID of the recipe.
        target_servings: The desired target number of servings (e.g. 2, 6, 8).
        base_servings: The original number of servings yielded by the recipe (default 4).

    Returns:
        A JSON string containing the recipe with scaled ingredient quantities.
    """
    if target_servings <= 0 or base_servings <= 0:
        return "Error: Servings must be positive numbers."

    scale_factor = target_servings / base_servings
    recipe_json = get_recipe(title_or_id)

    try:
        data = json.loads(recipe_json)
    except Exception:
        return recipe_json

    if not isinstance(data, dict) or "ingredients" not in data:
        return f"Recipe '{title_or_id}' not found in database."

    number_pattern = re.compile(r"^(\d+(?:\.\d+)?(?:\/\d+)?)\s*(.*)$")
    scaled_ingredients = []

    for ing in data.get("ingredients", []):
        match = number_pattern.match(ing.strip())
        if match:
            raw_qty, rest = match.groups()
            try:
                if "/" in raw_qty:
                    num, den = raw_qty.split("/")
                    val = float(num) / float(den)
                else:
                    val = float(raw_qty)
                scaled_val = round(val * scale_factor, 2)
                formatted_qty = int(scaled_val) if scaled_val.is_integer() else scaled_val
                scaled_ingredients.append(f"{formatted_qty} {rest}")
            except ValueError:
                scaled_ingredients.append(ing)
        else:
            scaled_ingredients.append(ing)

    result = {
        "title": data.get("title"),
        "base_servings": base_servings,
        "target_servings": target_servings,
        "scale_factor": scale_factor,
        "scaled_ingredients": scaled_ingredients,
        "instructions": data.get("instructions", []),
    }
    return json.dumps(result, indent=2)


def lookup_online_recipes(query: str) -> str:
    """Fetch real recipe ideas and cooking instructions from TheMealDB public API.

    Args:
        query: The meal name or main ingredient to search for (e.g., 'pasta', 'tacos', 'salmon', 'curry').

    Returns:
        A JSON string containing matching global recipes with ingredients, category, cuisine origin, and instructions.
    """
    if not query:
        return "Please provide a query term to search for online recipes."

    api_key = os.getenv("MEALDB_API_KEY", "1")
    url = "https://www.themealdb.com/api/json/v1/" + api_key + "/search.php"

    try:
        response = requests.get(url, params={"s": query}, timeout=8)
        response.raise_for_status()
        data = response.json()

        meals = data.get("meals")
        if not meals:
            return f"No online recipes found matching '{query}'."

        results = []
        for meal in meals[:3]:
            ingredients = []
            for i in range(1, 21):
                ing = meal.get(f"strIngredient{i}")
                meas = meal.get(f"strMeasure{i}")
                if ing and ing.strip():
                    measure_str = f"{meas.strip()} " if meas and meas.strip() else ""
                    ingredients.append(f"{measure_str}{ing.strip()}")

            results.append({
                "id": meal.get("idMeal"),
                "title": meal.get("strMeal"),
                "category": meal.get("strCategory"),
                "cuisine": meal.get("strArea"),
                "thumbnail": meal.get("strMealThumb"),
                "youtube_url": meal.get("strYoutube"),
                "ingredients": ingredients,
                "instructions": meal.get("strInstructions"),
            })

        return json.dumps(results, indent=2)
    except Exception as e:
        return f"Error fetching online recipes from API: {str(e)}"


def generate_dish_photo(
    prompt: str,
    tool_context: ToolContext,
) -> str:
    """Generate an AI presentation photo for a dish or recipe item, save it as an artifact, and upload it to public Cloud Storage.

    Args:
        prompt: Detailed description of the dish photo to generate (e.g. 'A delicious gourmet Creamy Tuscan Chicken garnished with fresh basil on a white plate').
        tool_context: ADK tool context injected automatically for saving artifacts.

    Returns:
        The public HTTPS URL of the uploaded dish image in Cloud Storage.
    """
    if not prompt:
        return "Error: Please provide a description for the dish image to generate."

    # Generate image using gemini-3.1-flash-lite-image in global region
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
    )

    image_bytes = None
    mime_type = "image/jpeg"

    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                if part.inline_data.mime_type:
                    mime_type = part.inline_data.mime_type
                break

    if not image_bytes:
        return "Error: Failed to generate image bytes from model."

    # 1. Save with tool_context.save_artifact so it shows up in Playground Artifacts panel
    filename = f"dish_photo_{uuid.uuid4().hex[:8]}.jpg"
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload image bytes directly to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return public_url



