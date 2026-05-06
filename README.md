## Setup
1. Download the model from [Google Drive](https://drive.google.com/drive/u/0/folders/1vXI6tYWkE0fMq5VB4CoxZyXnTZ7cxxcr)
2. Place it at `backend/models/distilbert/`
3. Run `pip install -r requirements.txt`

## How to Run in Docker

1. Launch Docker Desktop
2. Open Cloned Repository Folder
3. Build Docker image by running "docker build -t test-bot ." in Command Prompt
4. After building, run "docker run -p 10000:10000 test-bot"
