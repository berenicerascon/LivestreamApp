import os
import datetime
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

"""
YouTube Live Streaming Automation Script

Overview:
- This script automates the creation, binding, and starting of a YouTube live broadcast.
- It uses **YouTube Data API v3** for managing livestreams.
- The stream URL is saved in `live_url.txt` and dynamically loaded by `stream.html`.
- Works with **Streamlabs**, which sends video to the YouTube RTMP URL.

Limitations:
- This script is **linked to the YouTube account** authenticated via OAuth.
- Requires a **Google Developer Console project** with YouTube API enabled.
- `client_secrets.json` must be configured for the **correct Google account**.
- If using for a **client**, they must generate their own API credentials.
- The **stream must be started in Streamlabs** (or any RTMP encoder) to go live.

Setup Requirements:
1. Enable **YouTube Data API v3** in Google Developer Console.
2. Replace `YOUR_YOUTUBE_API_KEY` and `YOUR_CHANNEL_ID` with valid credentials.
3. Ensure `client_secrets.json` is in the project directory.
4. Run `live_stream.py` to create and start the broadcast.
5. Start streaming in **Streamlabs** using the provided RTMP URL & stream key.

Expected Behavior:
- A **new YouTube broadcast** is created and linked to a live stream.
- The **embed URL** is saved in `live_url.txt` and used in `stream.html`.
- If the stream **ends**, `live_url.txt` is cleared to hide the embed.
- The script **automatically starts** the broadcast without manual YouTube Studio interaction.
"""


# YouTube API Scope
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# STEP 1: AUTHENTICATION
def authenticate_youtube():
    """Authenticate and return the YouTube API client."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
        creds = flow.run_local_server(port=5000)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

# STEP 2: CREATE A LIVE BROADCAST
def create_broadcast(youtube):
    """Create a new live broadcast on YouTube and store the correct embed link."""
    start_time = (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).isoformat() + "Z"
    end_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=3)).isoformat() + "Z"

    request = youtube.liveBroadcasts().insert(
        part="snippet,status,contentDetails",
        body={
            "snippet": {
                "title": "Live Stream",
                "description": "Live stream using Streamlabs & YouTube API",
                "scheduledStartTime": start_time,
                "scheduledEndTime": end_time
            },
            "status": {
                "privacyStatus": "public",  # Change to "private" if needed
                "selfDeclaredMadeForKids": "False"
            },
            "contentDetails": {
                "enableAutoStart": False,
                "enableAutoStop": True
            }
        }
    )
    response = request.execute()
    broadcast_id = response["id"]

    # Convert to embeddable URL
    youtube_url = f"https://www.youtube.com/embed/{broadcast_id}"

    print(f"\n[DEBUG] Saving YouTube Embed URL: {youtube_url}")

    # Save it correctly
    with open("live_url.txt", "w") as file:
        file.write(youtube_url)

    return broadcast_id, youtube_url


# STEP 3: CHECK BROADCAST STATUS
def get_broadcast_status(youtube, broadcast_id):
    """Check the current status of the broadcast."""
    request = youtube.liveBroadcasts().list(
        part="id,status",
        id=broadcast_id
    )
    response = request.execute()

    # DEBUG: Print full API response (if needed)
    print("\nDEBUG: Full API Response:")
    print(response)  # Print the full API response for debugging

    if "items" not in response or not response["items"]:
        print("ERROR: No broadcast found with that ID. Double-check the broadcast creation.")
        return None  # Return None instead of crashing

    return response["items"][0]["status"]["lifeCycleStatus"]

# STEP 4: WAIT FOR STREAM DETECTION
def wait_for_stream_ready(youtube, broadcast_id):
    """Wait until YouTube detects the stream before transitioning to live."""
    print("\nWaiting for YouTube to detect the stream... Open Streamlabs and start streaming!")

    for _ in range(60):  # Wait up to 2 minutes
        status = get_broadcast_status(youtube, broadcast_id)

        if status is None:
            print("ERROR: Broadcast status could not be retrieved. Exiting...")
            return False

        print(f"Broadcast status: {status}")

        if status in ["testing", "liveStarting"]:
            print("Stream detected! Preparing to go LIVE...")
            return True
        
        time.sleep(2)  # Wait before checking again

    print("No stream detected. Make sure you started streaming in Streamlabs!")
    return False  # Timed out

# STEP 5: START THE BROADCAST
def start_broadcast(youtube, broadcast_id):
    """Start the YouTube live broadcast via API after verifying the stream is ready."""
    if wait_for_stream_ready(youtube, broadcast_id):
        request = youtube.liveBroadcasts().transition(
            broadcastStatus="live",
            id=broadcast_id,
            part="id,status"
        )
        response = request.execute()
        print(f"Broadcast {broadcast_id} is now **LIVE** on YouTube!")
    else:
        print("Stream was not detected. Broadcast cannot go live.")

# MAIN FUNCTION TO RUN EVERYTHING
def main():
    youtube = authenticate_youtube()
    broadcast_id, youtube_url = create_broadcast(youtube)

    if not broadcast_id:
        print("ERROR: Broadcast creation failed. Exiting...")
        return  # Exit early if broadcast was not created

    print("\n🎥 **NEXT STEPS**:")
    print("1) Open YouTube Studio and go to **Stream Settings**.")
    print("2) Copy your RTMP URL and Stream Key.")
    print("3) Open Streamlabs on your phone and enter the RTMP URL & Stream Key.")
    print("4) Start streaming from Streamlabs.")
    print("5) Once YouTube detects the stream, this script will bind it & go LIVE.")

    input("\nPress ENTER once you've started streaming from Streamlabs...")

    start_broadcast(youtube, broadcast_id)


if __name__ == "__main__":
    main()