import re
import json
from ast import literal_eval
import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.query import Query
from datetime import datetime
import requests
import random

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


# 🎯 Choose tone based on campaign target
def pick_tone_by_target(target):
    target = target.lower()
    tone_map = {
        "awareness": ["informative", "friendly", "soft promotional"],
        "growth": ["fomo", "promotional", "festive"],
        "engagement": ["friendly", "interactive", "fun"],
        "conversion": ["promotional", "fomo", "urgent"],
        "other": ["friendly", "promotional"]
    }
    return random.choice(tone_map.get(target, ["friendly", "promotional"]))


# Prompt builder with tone support
def build_prompt(description, target, business_name):
    tone = pick_tone_by_target(target)

    return (
        f"You are a WhatsApp marketing assistant creating engaging campaign messages.\n\n"
        f"  Business Name: {business_name}\n"
        f"  Description: {description}\n"
        f"  Goal: {target}\n"
        f"  Tone Style: {tone}\n\n"
        f"  Instructions:\n"
        f"- Generate 15 unique WhatsApp messages that match the business goal and tone.\n"
        f"- Each message must be under 250 characters.\n"
        f"- Include CTAs like 'Visit us', 'Try now', 'DM us', 'Check this out'.\n"
        f"- Include a placeholder link like https://missh.space.\n"
        f"- Return the result as a **JSON array of strings**.\n\n"
        f"  Output Format Example:\n"
        f'  ["Message 1", "Message 2", ..., "Message 15"]\n\n'
        f"  Only return the JSON list. No explanation or formatting."
    )


# Auto-update campaigns from ready-to-send ➜ ready after 1 day
def auto_update_ready_status():
    try:
        result = db.list_documents(
            database_id=DB_ID,
            collection_id=CAMPAIGN_COLLECTION_ID,
            queries=[Query.equal("status", ["ready-to-send"])]
        )
        for campaign in result["documents"]:
            gen_time_str = campaign.get("generated_at")
            if gen_time_str:
                try:
                    gen_time = datetime.fromisoformat(gen_time_str)
                    if datetime.now() - gen_time > timedelta(days=1):
                        db.update_document(
                            database_id=DB_ID,
                            collection_id=CAMPAIGN_COLLECTION_ID,
                            document_id=campaign["$id"],
                            data={"status": "ready"}
                        )
                        print(f"⏩ Auto-updated campaign '{campaign['business_name']}' to 'ready'")
                except Exception as e:
                    print("⚠️ Error parsing date or updating status:", e)
    except Exception as e:
        print("❌ Failed to fetch ready-to-send campaigns:", e)


# Get all ready campaigns
def list_ready_campaigns():
    try:
        result = db.list_documents(
            database_id=DB_ID,
            collection_id=CAMPAIGN_COLLECTION_ID,
            queries=[Query.equal("status", ["ready"])]
        )
        return result["documents"]
    except Exception as e:
        print("❌ Failed to list campaigns:", e)
        return []


# User selects campaign
def choose_campaign(campaigns):
    print("\nReady Campaigns:\n")
    for i, camp in enumerate(campaigns):
        name = camp.get("business_name", "Unnamed")
        desc = camp.get("description", "")
        print(f"{i+1}. {name} - {desc[:40]}...  (ID: {camp['$id']})")
    try:
        choice = int(input("\n Enter the number of the campaign to generate messages for: ")) - 1
        if 0 <= choice < len(campaigns):
            return campaigns[choice]
        else:
            print("❌ Invalid choice.")
            return None
    except ValueError:
        print("❌ Please enter a valid number.")
        return None

# 📥 Get campaign with status = "ready"
def get_ready_campaign():
    try:
        result = db.list_documents(
            database_id=DB_ID,
            collection_id=CAMPAIGN_COLLECTION_ID,
            queries=[Query.equal("status", ["ready"])]
        )
        if result["total"] > 0:
            return result["documents"][0]
        return None
    except Exception as e:
        print("❌ Appwrite query error:", e)
        return None


# Update campaign with generated messages
def update_campaign_messages(campaign_id, messages):
    try:
        db.update_document(
            database_id=DB_ID,
            collection_id=CAMPAIGN_COLLECTION_ID,
            document_id=campaign_id,
            data={
                "messages": messages,
                "status": "ready-to-send",
                "generated_at": datetime.now().isoformat()
            }
        )
    except Exception as e:
        print("❌ Failed to update campaign:", e)


# 🤖 Generate AI messages from Ollama
def generate_messages(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )
        result = response.json()
        content = result.get("response", "").strip()

        print("🔎 Raw response from Ollama:\n", content)

        # 🛠️ Fix for missing commas between list elements
        if content.startswith("[") and content.endswith("]"):
            # Add comma between each closing quote and next opening quote
            fixed_content = re.sub(r'"\s*"', '", "', content)
            try:
                parsed = literal_eval(fixed_content)
                if isinstance(parsed, list):
                    return list({msg.strip() for msg in parsed if isinstance(msg, str) and msg.strip()})
            except Exception as e:
                print(f"⚠️ Failed to parse fixed list: {e}")

        print("⚠️ No valid list structure detected.")
        return []

    except Exception as e:
        print(f"❌ Failed to generate messages with Ollama: {e}")
        return []


# Main runner
def run():
    campaigns = list_ready_campaigns()
    if not campaigns:
        print("🚫 No campaigns with 'ready' status found.")
        return

    selected_campaign = choose_campaign(campaigns)
    if not selected_campaign:
        return

    print(f"\n✍️ Generating messages for: {selected_campaign['business_name']}")

    description = selected_campaign.get("description", "")
    target = selected_campaign.get("target", "Awareness")
    business_name = selected_campaign.get("business_name", "Your Brand")

    prompt = build_prompt(description, target, business_name)
    messages = generate_messages(prompt)

    if messages:
        update_campaign_messages(selected_campaign["$id"], messages)
        print(f"✅ {len(messages)} AI messages generated and saved to campaign.")
    else:
        print("⚠️ No messages generated.")


if __name__ == "__main__":
    run()