import os
import datetime
import time
import random
import calendar
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Instructions:

# Log in to YouTube on StreamLabs
# Run script, pick title and desired time to stream
# Press Go Live in StreamLabs, select YouTube, choose "Upcoming event"
# Select the right broadcast, go live
    # If you get an error, you need to force quit the app and try again
    # It should work now
# Look at stream page on localhost, after a few seconds the stream should pop up :)

# YouTube API Scope
SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

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

def prompt_broadcast_details():
    """Prompt user for broadcast title, date, and time."""
    title = input("Enter the broadcast title: ").strip()

    while True:
        try:
            # Get current UTC date and time
            now = datetime.datetime.utcnow()
            year = now.year  # Keep everything in the current year

            # Select month (1-12)
            month = int(input(f"Enter the month (1-12): ").strip())
            if month < 1 or month > 12:
                raise ValueError("Invalid month")

            # Get correct max days for the selected month
            max_days = calendar.monthrange(year, month)[1]

            # Select day (1-max_days)
            day = int(input(f"Enter the day (1-{max_days}): ").strip())
            if day < 1 or day > max_days:
                raise ValueError(f"Invalid day! The selected month has {max_days} days.")

            # Select time (HH:MM)
            time_input = input("Enter start time (HH:MM in 24-hour format, e.g., 15:30): ").strip()
            start_time = datetime.datetime.strptime(time_input, "%H:%M").time()

            # Combine selected date and time
            scheduled_start = datetime.datetime(year, month, day, start_time.hour, start_time.minute)

            # Fixing UTC early start if necessary
            min_future_time = now + datetime.timedelta(minutes=1)
            if scheduled_start < min_future_time:
                print("Fixing UTC time ...")
                scheduled_start = min_future_time

            # Debugging output
            print("\n DEBUG INFO:")
            print(f"Current UTC Time: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"User Selected Date & Time: {scheduled_start.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"Minimum Allowed Start Time: {min_future_time.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f"Final Scheduled Start Time: {scheduled_start.strftime('%Y-%m-%d %H:%M UTC')}\n")

            return title, scheduled_start
        except ValueError as e:
            print(f"Invalid input: {e}. Please enter a valid month, day, and time.")

def create_broadcast(youtube, title, scheduled_start, max_retries=5):
    """Create a new YouTube live broadcast, retrying on errors."""
    start_time = scheduled_start.isoformat() + "Z"
    end_time = (scheduled_start + datetime.timedelta(hours=3)).isoformat() + "Z"

    print(f"\n[DEBUG] Sending start time to YouTube API: {start_time}")
    print(f"[DEBUG] End time for broadcast: {end_time}")

    retries = 0
    while retries < max_retries:
        try:
            request = youtube.liveBroadcasts().insert(
                part="snippet,status,contentDetails",
                body={
                    "snippet": {
                        "title": title,
                        "description": f"Live stream: {title}",
                        "scheduledStartTime": start_time,
                        "scheduledEndTime": end_time
                    },
                    "status": {
                        "privacyStatus": "public",
                        "selfDeclaredMadeForKids": False
                    },
                    "contentDetails": {
                        "enableAutoStart": False,
                        "enableAutoStop": True
                    }
                }
            )
            response = request.execute()
            broadcast_id = response["id"]
            youtube_url = f"https://www.youtube.com/embed/{broadcast_id}"

            print(f"\n Broadcast '{title}' scheduled at {scheduled_start.strftime('%Y-%m-%d %H:%M UTC')}")
            print(f" Watch Live: {youtube_url}")

            with open("live_url.txt", "w") as file:
                file.write(youtube_url)

            return broadcast_id, youtube_url
        except HttpError as e:
            error_message = str(e)
            print(f"ERROR: {error_message}")

            if "503" in error_message:
                wait_time = random.randint(5, 15)
                print(f"YouTube API is temporarily unavailable. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                break  # Stop retrying if it's not a 503 error

    print("ERROR: Unable to schedule broadcast after multiple attempts.")
    return None, None

def main():
    youtube = authenticate_youtube()
    
    # Prompt user for broadcast title and time
    title, scheduled_start = prompt_broadcast_details()
    
    broadcast_id, youtube_url = create_broadcast(youtube, title, scheduled_start)

    if not broadcast_id:
        print("ERROR: Broadcast creation failed. Exiting...")
        return
    
    print("\n**NEXT STEPS**:")
    print("1) Open Streamlabs and select the scheduled YouTube event.")
    print("2) Wait for stream start time.")
    print("3) Start streaming in StreamLabs and it should go live in a few seconds!")

if __name__ == "__main__":
    main()
