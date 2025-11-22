# ==========================================
# STAGE 1: The Frontend Factory (Node.js)
# ==========================================
# Use a Node image solely to build the React static files.
# Once built, this stage is discarded to save space.
# STAGE 1: Build React
FROM node:20 AS build-step
WORKDIR /app

# 1. Copy ONLY the package.json (Ignore the lock file for now)
COPY ./frontend/package.json ./

# 2. Install dependencies FRESH (This avoids Windows/Linux conflicts)
RUN npm install

# 3. Copy the rest and build
COPY ./frontend ./
RUN npm run build

# ==========================================
# STAGE 2: The Production Server (Python)
# ==========================================
# Switch to a lightweight Python image for the final app.
FROM python:3.9-slim

# 1. Set up the server folder
WORKDIR /app

# 2. Update Linux and install the C++ Compiler (gcc)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 3. Upgrade pip
RUN pip install --upgrade pip

# 4. Copy Backend requirements
COPY ./backend/requirements.txt ./

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. DOWNLOAD NLP MODEL
# Done during the build so the model is ready immediately on startup.
# RUN python -m spacy download en_core_web_sm

# 7. Copy the Backend Source Code
COPY ./backend ./

# 8. IMPORT REACT BUILD
# Copy the static files FROM Stage 1 into a folder named 'client'
COPY --from=build-step /app/dist ./client

# 9. Configuration
# Render expects port 10000
EXPOSE 10000

# 10. Start Command (Optimized for 15-100 Users)
# -w 2: Two worker processes
# --threads 4: Four concurrent threads per worker
# app:app : Points to 'app.py' file and the 'app' flask object inside it
CMD ["gunicorn", "-w", "2", "--threads", "4", "-b", "0.0.0.0:10000", "app:app"]