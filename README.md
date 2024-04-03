Setup Guide:

Environment:

Python Version: 3.10.11

pip Version: 24.0

Setup Steps:

Enter your OPENAI_API_KEY and SERP_API_KEY in a separate .env file.

Create a new file named .env in the project directory.

Open the .env file and add the following lines, 

replacing <OPENAI_API_KEY> and <SERP_API_KEY> with your actual API keys:

OPENAI_API_KEY=<your_openai_api_key>

SERP_API_KEY=<your_serp_api_key>

[Optional] Create and activate a virtual environment or conda environment.

Virtual Environment:

Create a virtual environment:
python -m venv venv

Activate the virtual environment:


For Windows:
venv\Scripts\activate
For macOS/Linux:
source venv/bin/activate

Conda Environment:

Create a conda environment:
conda create --name myenv python=3.10.11

Activate the conda environment:
conda activate myenv

Replace myenv with the desired name for your environment.

Install the required libraries:
pip install -r requirements.txt


Start the project:

python main.py

