import os
path = "notebooks/chroma_db_"
if os.path.exists("notebooks/chroma_db_"):
    print("Running in notebook environment")
    print(os.listdir(path))