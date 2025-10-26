import os
import time
import random
from dotenv import load_dotenv
from datetime import datetime
import pywhatkit as kit
from appwrite.services.databases import Databases
from appwrite.query import Query
from appwrite.client import Client

# Load environment variables
load_dotenv()

# Appwrite setup
client = Client()
client.set_endpoint(os.getenv("APPWRITE_ENDPOINT"))
client.set_project(os.getenv("APPWRITE_PROJECT_ID"))
client.set_key(os.getenv("APPWRITE_API_KEY"))

db = Databases(client)

DB_ID = os.getenv("APPWRITE_DATABASE_ID")
CAMPAIGN_COLLECTION_ID = os.getenv("CAMPAIGNS_COLLECTION_ID")
WHATSAPP_COLLECTION_ID = os.getenv("WHATSAPP_CONTACTS_COLLECTION_ID")
DELAY = int(os.getenv("DELAY_BETWEEN_MSGS", 15))
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"

# Get campaign
def get_ready_campaign():
    try:
        result = db.list_documents(
            database_id=DB_ID,
            collection_id=CAMPAIGN_COLLECTION_ID,
            queries=[Query.equal("status", "ready-to-send")]
        )
        return result["documents"][0] if result["total"] > 0 else None
    except Exception as e:
        print("❌ Appwrite query error:", e)
        return None

# Get contacts
def get_contacts():
    try:
        result = db.list_documents(
            database_id=DB_ID,
            collection_id=WHATSAPP_COLLECTION_ID
        )
        return result["documents"]
    except Exception as e:
        print("❌ Failed to fetch contacts:", e)
        return []

# Add CTA
def add_cta(message, link):
    if "http" not in message:
        return f"{message} 👉 {link}"
    return message

# Mark campaign as sent
def mark_campaign_sent(campaign_id):
    try:
        db.update_document(
            database_id=DB_ID,
            collection_id=CAMPAIGN_COLLECTION_ID,
            document_id=campaign_id,
            data={"status": "sent"}
        )
    except Exception as e:
        print("❌ Failed to update campaign status:", e)

# Send message instantly
def send_message(phone, message):
    try:
        print(f"⏳ Sending message to {phone} now...")
        kit.sendwhatmsg_instantly(phone, message, wait_time=15, tab_close=True)
        time.sleep(DELAY)
        print(f"✅ Message sent to {phone}")
    except Exception as e:
        print(f"❌ Failed to send message to {phone}: {e}")

# Main runner
def run():
    campaign = get_ready_campaign()
    if not campaign:
        print("🚫 No campaign with 'ready-to-send' status found.")
        return

    print(f"📤 Launching campaign for: {campaign.get('business_name', 'Your Brand')}")
    messages = campaign.get("messages", [])
    link = campaign.get("link", "https://instagram.com/chai")
    contacts = get_contacts()

    if not messages:
        print("⚠️ No messages found in campaign.")
        return

    if not contacts:
        print("🚫 No contacts found.")
        return

    if TEST_MODE:
        contact = contacts[0]
        phone = contact.get("number", "")  # ✅ FIXED HERE
        if not phone.startswith("+"):
            phone = "+91" + phone
        message = random.choice(messages)
        send_message(phone, add_cta(message, link))
        return

    for contact in contacts:
        name = contact.get("name", "Unknown")
        phone = contact.get("number", "")  # ✅ FIXED HERE
        print(f"📞 Found contact: {name} - Raw number: {phone}")
        if not phone:
            continue
        if not phone.startswith("+"):
            phone = "+91" + phone
        message = random.choice(messages)
        send_message(phone, add_cta(message, link))

    mark_campaign_sent(campaign["$id"])
    print("✅ Campaign marked as sent.")

if __name__ == "__main__":
    run()

