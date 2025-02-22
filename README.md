# AI-Powered KYC (Know Your Customer) System  

This is an AI-powered KYC system designed to verify customer identities with multiple verification layers.  

## Features  

The system consists of several verification layers:  
- **OCR Verification** – Extracts and validates text from ID documents from given form data.  
- **Metadata Verification** – Checks image metadata for inconsistencies.  
- **ELA (Error Level Analysis) Check** – Detects possible image tampering.  
- **Photo Forensics** – Performs in-depth pixel and pattern analysis.  
- **Decision-Making Engine** – Aggregates verification results and uses AI to make a final decision based on priority and confidence levels.  

## How It Works  

Each verification layer outputs its results individually. These results are then passed to an AI engine, which determines the final decision based on predefined rules and priority settings.  

## Installation  

Follow these steps to set up and run the project:  

1. **Clone the repository**  
   ```bash
   git clone <repository-url>
   cd <project-folder>
2. **Install dependencies**
    ```bash
   pip install -r requirements.txt
3. **Set up environment variables**
- Create a .env file in the project root.
- Paste the required environment variables and fill in the actual values.

4. **Run the application**
    ```bash
   py app.py

The user interface is minimal but functional—it gets the job done!
![KYC System](assets/kyc_system.png)
