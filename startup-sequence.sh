# 1. Create the project structure
mkdir -p semantic-query-agent/database/init
cd semantic-query-agent

# 2. Place all files in their locations (see table above)
# 3. Edit .env — add your real OPENAI_API_KEY

# 4. Start the stack
docker compose up -d

# 5. Watch logs until healthy
docker compose ps

# 6. Run the verifier (from your local Python env or WSL2)
pip install -r requirements.txt
python verify_setup.py