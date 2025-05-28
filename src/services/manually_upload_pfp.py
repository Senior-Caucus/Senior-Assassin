from .drive import upload_profile_picture

email = "ema50@stuy.edu"
filepath = "/home/seahorse/Senior-Assassin/src/services/profile_pic.jpg"

def upload_user_profile_picture(email: str, filepath: str):
    """
    Upload a user's profile picture to Google Drive.
    
    :param email: User's email address.
    :param filepath: Path to the profile picture file.
    :return: The file ID of the uploaded picture.
    """
    return upload_profile_picture(email, filepath, "image/jpeg")
if __name__ == "__main__":
    file_id = upload_user_profile_picture(email, filepath)
    print(f"Uploaded profile picture for {email} with file ID: {file_id}")
