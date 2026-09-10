from pathlib import Path


# List of the Folders

folders = [
    "src",
    "documents",
    "templates",
    "static",
    "uploads",
    "data",
]


# List of the Files

files = [
    # Root files
    "app.py",
    "data_ingestion.py",
    "requirements.txt",
    "Dockerfile",
    ".env",

    # Source files
    "src/__init__.py",
    "src/config.py",
    "src/db.py",
    "src/ingestion.py",
    "src/models.py",
    "src/self_rag.py",
    "src/vectorstore.py",

    # Frontend
    "templates/index.html",
    "static/styles.css",
    "static/app.js",
]


def create_project_structure():
    # Create folders
    for folder in folders:
        Path(folder).mkdir(parents=True, exist_ok=True)

    # Create files
    for file in files:
        Path(file).touch(exist_ok=True)


    print("Project structure created successfully!")


if __name__ == "__main__":
    create_project_structure()