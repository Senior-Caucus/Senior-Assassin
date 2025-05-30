import os
from .drive import upload_profile_picture

# Path to the folder with profile pictures
image_dir = "/home/seahorse/Senior-Assassin/src/services/drive_pictures"

def upload_all_profile_pictures():
    for filename in os.listdir(image_dir):
        if filename.endswith(".jpg"):
            email_prefix = filename.replace(".jpg", "")
            email = f"{email_prefix}@stuy.edu"
            filepath = os.path.join(image_dir, filename)
            
            try:
                file_id = upload_profile_picture(email, filepath, "image/jpeg")
                print(f"Uploaded profile picture for {email} with file ID: {file_id}")
            except Exception as e:
                print(f"Failed to upload {email}: {e}")

if __name__ == "__main__":
    upload_all_profile_pictures()