import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Safety check
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or Key not set. Check your .env file.")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test connection (optional)
try:
    response = supabase.table("resumes").select("*").limit(1).execute()
    print("Supabase connection successful:", response.data)
except Exception as e:
    print("Error connecting to Supabase:", e)
