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
from tqdm import tqdm
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor

INPUT_FILE = 'mtgdataset/data/autotagging.tsv'
TRACKS, TAGS, EXTRA = read_file(INPUT_FILE)
DB = Database('faiss_index', True)


def download_and_post(download_dir, song_metadata,
                      download_suffix=".crdownload", wait_time=10, start_buffer=0):
    print(f"Downloading {song_metadata['title']}!")
    # wait for download
    filename_prefix = song_metadata['title'].replace(" ", "_")
    filepath = None

    t = 0
    time.sleep(start_buffer)

    # Wait for the download to start
    matching_files = None
    while True:
        files = os.listdir(download_dir)
        matching_files = [
            f for f in files if f.startswith(filename_prefix)]
        if matching_files:
            break
        time.sleep(0.5)
        t += 0.5
        if t >= wait_time:
            print("Failed to find file for download", filename_prefix)
            return

    # get most recent matching file
    matching_files = [os.path.join(download_dir, f)
                      for f in matching_files]
    matching_files.sort(
        key=lambda x: os.path.getmtime(x), reverse=True)
    current_file = matching_files[0]
    if current_file.endswith(download_suffix):
        current_file = current_file[:-len(download_suffix)]

    # Wait for the download to complete
    while not os.path.exists(current_file):
        time.sleep(0.5)
        t += 0.5
        if t >= wait_time:
            print("Failed to download file", current_file)
            return

    # post to DB
    song_object = Song(song_metadata['title'],
                       current_file, artist=song_metadata['artist'],
                       url=song_metadata['url'],
                       description=song_metadata['description'])
    DB.post_songs([song_object])

    # clean-up
    os.remove(current_file)
    print(
        f"Downloaded and posted {song_metadata['title']} in {t:.2f} sectionsfrom directory {current_file}!")


def download_song(track_id_list, download_wait_time=30, min_threads=2, max_threads=3):
    download_dir = os.path.abspath("backend/temp_audio")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    caps = DesiredCapabilities.CHROME
    caps["goog:loggingPrefs"] = {"performance": "ALL"}
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

        # Wait for the login window to appear
        WebDriverWait(driver, 4).until(
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
        CHROME_USER = os.getenv("CHROME_USER")
        CHROME_PASSWORD = os.getenv("CHROME_PASSWORD")

        # Enter your log-in info
        email_field.send_keys(CHROME_USER)
        password_field.send_keys(CHROME_PASSWORD)

        # Locate the log-in button
        submit_button = driver.find_element(
            By.XPATH, "//button[@type='submit' and contains(@class, 'btn btn--brand btn--lg js-signin-form')]")

        # Use Javascript to click the log in button
        driver.execute_script("arguments[0].click();", submit_button)

        # Wait a bit to make sure that you are logged in
        time.sleep(0.2)
        # print("Login completed!")
        # print("Logged in successfully!")
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = deque()
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
                download_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.CLASS_NAME, "js-overlay-download"))
                )

                # Click the Free Download button
                download_button.click()
                time.sleep(0.2)

                song_metadata = {
                    "title": song_title,
                    "artist": artist,
                    "url": url,
                    "description": ""
                }
                # add download thread
                futures.append(executor.submit(download_and_post, download_dir,
                                               song_metadata, wait_time=download_wait_time))

                if len(futures) >= max_threads:
                    while len(futures) > min_threads:
                        futures.popleft().result()

        # Next step: Format download into song objects!
        # Push the song object to the database!
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(elapsed_time)
        DB.save_db()

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

    finally:
        driver.quit()
        
if __name__ == "__main__":
    track_ids = list(TRACKS.keys())

    one_track_id = [track_ids[0]]
    first_track = TRACKS[one_track_id[0]]

    track_id_list = track_ids[:100]

    # Run the download_song feature using this function
    download_song(track_id_list)
