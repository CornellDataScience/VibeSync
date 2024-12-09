from commons import read_file
from database import Database
from songs import Song
import traceback
import time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from dotenv import load_dotenv
import os


input_file = 'mtgdataset/data/autotagging.tsv'
tracks, tags, extra = read_file(input_file)

# print("Tracks:", tracks)
# print("---------------------------------")

# Lets only save a few track ids so that we can start web scrapping


def get_track_ids(tracks):
    return list(tracks.keys())


track_ids = get_track_ids(tracks)
# print("Tracks without info:", track_ids)


def download_song(track_id_list):

    # Initialize the database
    db = Database('faiss_index', True)

    # Specify and create the download directory
    download_dir = os.path.abspath("backend/temp_audio")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    caps = DesiredCapabilities.CHROME
    caps["goog:loggingPrefs"] = {"performance": "ALL"}

    # Set Chrome preferences for the download directory
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,  # Set custom download directory
        "download.prompt_for_download": False,       # Disable download prompt
        "directory_upgrade": True,                   # Automatically overwrite
        "safebrowsing.enabled": True                 # Enable safe browsing
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)

    start_time = time.time()

    try:
        driver.get("https://www.jamendo.com/start")
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Log in')]"))
        )
        login_button.click()
        # print("LOG IN button clicked!")

        # Wait for the login window to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//input[@name='email']"))
        )

        # Find the email and password fields, find the log in button
        email_field = driver.find_element(By.XPATH, "//input[@name='email']")
        password_field = driver.find_element(
            By.XPATH, "//input[@name='password']")
        submit_button = driver.find_element(
            By.XPATH, "//button[contains(text(), 'Log in')]")

        # Load environment variables from .env file
        load_dotenv(override=True)

        # Access environment variables
        CHROME_USER = os.getenv("CHROME_USER")
        CHROME_PASSWORD = os.getenv("CHROME_PASSWORD")

        # Enter you log in info
        email_field.send_keys(CHROME_USER)
        password_field.send_keys(CHROME_PASSWORD)

        # Locate the log in button
        submit_button = driver.find_element(
            By.XPATH, "//button[@type='submit' and contains(@class, 'btn btn--brand btn--lg js-signin-form')]")

        # Use Javascript to click the log in button
        # print("Click the log in button")
        driver.execute_script("arguments[0].click();", submit_button)

        # Wait a bit to make sure that you are logged in
        time.sleep(0.2)
        # print("Login completed!")
        # print("Logged in successfully!")

        for id in track_id_list:
            # Define the url to the track_id
            url = "https://www.jamendo.com/track/" + str(id)

            driver.get(url)

            # Wait for the Download button to load
            # print("Waiting for the Download button")
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "js-abtesting-trigger-start"))
            )

            # Click the Download button
            # print("Clicking the download button")
            download_button.click()
            # print("Download button clicked")

            song_title_element = driver.find_element(
                By.XPATH, "//h1[@class='primary']/span")
            song_title = song_title_element.text

            artist_name_element = driver.find_element(
                By.XPATH, "//a[@class='secondary']/span")
            artist = artist_name_element.text

            # Wait for the download button to load
            # print("Waiting for the free download button to load")
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CLASS_NAME, "js-overlay-download"))
            )

            # Click the Free Download button
            # print("Clicking the free download button")
            download_button.click()
            # print("Free download button clicked")

            time.sleep(0.2)

            print("Downloaded:" + str(id))

            song_title_underscored = song_title.replace(" ", "_")
            artist_underscored = artist.replace(" ", "_")

            filename = song_title_underscored

            # print(song_title_underscored)

            files = os.listdir(download_dir)

            def wait_for_download(download_dir, filename_prefix):
                current_file = ".crdownload"  # Initialize to trigger the loop

                while True:
                    # List files in the directory
                    files = os.listdir(download_dir)

                    # Filter files starting with the prefix
                    matching_files = [
                        f for f in files if f.startswith(filename_prefix)]

                    # If no matching files are found, keep waiting
                    if not matching_files:
                        print("Waiting for file to appear...")
                        time.sleep(0.1)
                        continue

                    # Get full file paths
                    matching_files = [os.path.join(
                        download_dir, f) for f in matching_files]

                    # Sort files by last modified time in descending order
                    matching_files.sort(
                        key=lambda x: os.path.getmtime(x), reverse=True)

                    # Get the most recent file
                    current_file = matching_files[0]

                    # Check if the file still ends with ".crdownload"
                    if current_file.endswith(".crdownload"):
                        print(f"File is still downloading: {current_file}")
                        time.sleep(0.1)  # Wait and continue checking
                    else:
                        print(f"Download complete: {current_file}")
                        return current_file

            latest_file_path = wait_for_download(
                download_dir, song_title_underscored)
            print(latest_file_path)

            song_object = Song(song_title, latest_file_path)
            db.post_songs([song_object])

            # print(filename)
            # path = os.path.join (download_dir, filename)
            # title = os.path.splitext(filename)[0].lower().replace('_', " ")
            # songs.append(Song(title, path))
            # print((title, path))

        # Next step: Format download into song objects!
        # Push the song object to the database!
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(elapsed_time)
        db.save_db()

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

# TO USE THE ABOVE FUNCTION:


# First, specify a list of track ids
one_track_id = [track_ids[0]]
first_track = tracks[one_track_id[0]]

track_id_list = track_ids[:10]

# Run the download_song feature using this function
download_song(track_id_list)
