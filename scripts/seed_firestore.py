from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-abe3a9744f22"


def seed_recipes():
    db = firestore.Client(project=PROJECT_ID)
    recipes_ref = db.collection("recipes")

    sample_recipes = [
        {
            "title": "Cilantro Lime Chicken Thighs",
            "category": "Mexican",
            "prep_time_mins": 10,
            "cook_time_mins": 20,
            "is_gluten_free": True,
            "is_dairy_free": True,
            "ingredients": [
                "1.5 lbs chicken thighs",
                "1/4 cup fresh cilantro chopped",
                "2 fresh limes juiced",
                "2 tbsp olive oil",
                "1 tsp garlic powder",
                "1/2 tsp salt",
                "1/4 tsp black pepper",
            ],
            "instructions": [
                "In a bowl, combine lime juice, cilantro, olive oil, garlic powder, salt, and pepper.",
                "Marinate chicken thighs for 15 minutes.",
                "Heat skillet over medium-high heat and sear chicken for 6-8 minutes per side until cooked through.",
                "Garnish with extra fresh cilantro and lime wedges.",
            ],
        },
        {
            "title": "Gluten-Free Creamy Tuscan Chicken",
            "category": "Italian",
            "prep_time_mins": 15,
            "cook_time_mins": 20,
            "is_gluten_free": True,
            "is_dairy_free": False,
            "ingredients": [
                "1 lb chicken breast cutlets",
                "1/2 cup sun-dried tomatoes",
                "2 cups fresh spinach",
                "3/4 cup heavy cream",
                "1/2 cup chicken broth",
                "3 cloves garlic minced",
                "1/2 cup grated parmesan cheese",
            ],
            "instructions": [
                "Season chicken breasts and pan-fry in olive oil until golden brown. Remove and set aside.",
                "Sauté garlic and sun-dried tomatoes in the same pan.",
                "Pour in chicken broth and heavy cream, bring to a gentle simmer.",
                "Stir in parmesan cheese and spinach until wilted.",
                "Return chicken to the sauce and simmer for 3 minutes before serving.",
            ],
        },
        {
            "title": "Thai Basil Chicken Stir-Fry",
            "category": "Asian",
            "prep_time_mins": 10,
            "cook_time_mins": 10,
            "is_gluten_free": True,
            "is_dairy_free": True,
            "ingredients": [
                "1 lb ground chicken",
                "1 cup fresh Thai basil leaves",
                "3 cloves garlic minced",
                "2 Thai chili peppers sliced",
                "2 tbsp tamari (gluten-free soy sauce)",
                "1 tbsp fish sauce",
                "1 tsp coconut sugar",
            ],
            "instructions": [
                "Sauté garlic and chili peppers in oil for 30 seconds until fragrant.",
                "Add ground chicken and cook through, breaking into small pieces.",
                "Stir in tamari, fish sauce, and coconut sugar.",
                "Turn off heat and fold in fresh basil leaves until wilted. Serve hot with rice.",
            ],
        },
    ]

    for recipe in sample_recipes:
        doc_id = recipe["title"].lower().replace(" ", "-")
        recipes_ref.document(doc_id).set(recipe)
        print(f"Seeded recipe: {recipe['title']} (ID: {doc_id})")


if __name__ == "__main__":
    seed_recipes()
