# TextSpark – AI WhatsApp Marketing Automation Platform

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Appwrite](https://img.shields.io/badge/Appwrite-Database-orange)
![License](https://img.shields.io/badge/License-MIT-green)

**TextSpark** is an AI-powered WhatsApp marketing automation tool that generates personalized messages for campaigns using GPT/Ollama APIs and sends them automatically using PyWhatKit. It helps businesses streamline campaigns, boost engagement, and save time.

---

## 🚀 Features

- Generate 25+ personalized messages per campaign using AI
- Automatically send messages via WhatsApp Web
- Dynamic CTA (links) appended to messages
- Test mode to safely send messages to a single contact before full deployment
- Logs campaign status and ensures campaigns are sent only once
- Integrates with Appwrite for campaign and contact management

---

## 🛠️ Tech Stack

- **Backend:** Python  
- **APIs:** OpenAI / Ollama GPT  
- **Automation:** PyWhatKit  
- **Database:** Appwrite (Databases & Collections)  
- **Environment Management:** dotenv  

---

## ⚡ Setup Instructions

### 1. Install dependencies

```bash```
pip install -r requirements.txt

### 2. Create a .env file
Add your Appwrite and configuration details:

```env```
APPWRITE_ENDPOINT=https://<your-appwrite-endpoint>
APPWRITE_PROJECT_ID=<your-project-id>
APPWRITE_API_KEY=<your-api-key>
APPWRITE_DATABASE_ID=<your-database-id>
CAMPAIGNS_COLLECTION_ID=<your-campaigns-collection-id>
WHATSAPP_CONTACTS_COLLECTION_ID=<your-contacts-collection-id>
DELAY_BETWEEN_MSGS=15
TEST_MODE=true

### 3. Run the script
```bash```
python main.py

TEST_MODE=true: Only the first contact will receive a message
TEST_MODE=false: All contacts in the WhatsApp collection will receive messages

### 📁 Project Structure
textspark/
│
├── main.py              # Core script for sending WhatsApp messages
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not committed)
└── README.md

###  ⚙️ How It Works
Fetches a campaign with status ```ready-to-send``` from Appwrite

Retrieves all contacts from the WhatsApp contacts collection

Randomly selects a personalized message from the campaign

Appends a CTA link if missing

Sends the message via WhatsApp Web using PyWhatKit

Marks the campaign as ```sent``` in Appwrite

### 💡 Notes & Recommendations
Ensure WhatsApp Web is logged in and accessible on your machine

Adjust DELAY_BETWEEN_MSGS to avoid WhatsApp restrictions

Test campaigns first using TEST_MODE=true

Optionally, log sent messages to a separate Appwrite collection for tracking






