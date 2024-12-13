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
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from numpy import random
random.seed(42)
TRACKS, TAGS, EXTRA = read_file('mtgdataset/data/autotagging.tsv')
DB = Database(f'full_jamendo', True)


def download_and_post(download_dir, song_metadata,
                      download_suffix=".crdownload", wait_time=10, start_buffer=0.5):
    # wait for download
    filename_prefix = song_metadata['title'].replace(" ", "_")
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
    id = song_metadata['id']
    track = TRACKS[id]
    song_object = Song(song_metadata['title'],
                       current_file, str(id), artist=song_metadata['artist'],
                       url=song_metadata['url'],
                       genre=track['genre'],
                       duration=track['duration'],
                       instrument=track['instrument'],
                       moodtheme=track['mood/theme'],
                       description=song_metadata['description'])
    DB.post_songs([song_object])
    if os.path.exists(current_file):
        os.remove(current_file)


def download_song(track_id_list, download_wait_time=30, min_threads=1, max_threads=2, process=1):
    download_dir = os.path.abspath(f"backend/audio/{process}")
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

    try:
        idx = 0
        driver.get("https://www.jamendo.com/start")
        login_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Log in')]"))
        )
        login_button.click()

        # Wait for the login window to appear
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@name='email']"))
            )
        except Exception as e:
            print("Failed to load login page")
            return

        # Find the email and password fields, find the log in button
        email_field = driver.find_element(By.XPATH, "//input[@name='email']")
        password_field = driver.find_element(
            By.XPATH, "//input[@name='password']")
        submit_button = driver.find_element(
            By.XPATH, "//button[contains(text(), 'Log in')]")

        # Load environment variables from .env file
        process_suffix = f"_{process}" if process > 1 else ""
        load_dotenv(override=True)
        email = os.getenv("CHROME_USER"+process_suffix)
        password = os.getenv("CHROME_PASSWORD"+process_suffix)

        # Enter your log-in info
        email_field.send_keys(email)
        password_field.send_keys(password)

        # Locate the log-in button
        submit_button = driver.find_element(
            By.XPATH, "//button[@type='submit' and contains(@class, 'btn btn--brand btn--lg js-signin-form')]")

        # Use Javascript to click the log in button
        driver.execute_script("arguments[0].click();", submit_button)

        # Wait a bit to make sure that you are logged in
        time.sleep(2)
        # print("Login completed!")
        # print("Logged in successfully!")
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = deque()
            for idx, id in enumerate(track_id_list):
                # Define the url to the track_id
                url = "https://www.jamendo.com/track/" + str(id)

                driver.get(url)

                # Wait for the Download button to load
                # print("Waiting for the Download button")
                download_button = None
                try:
                    download_button = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable(
                            (By.CLASS_NAME, "js-abtesting-trigger-start"))
                    )
                except Exception as e:
                    continue

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
                try:
                    download_button = WebDriverWait(driver, 0.2).until(
                        EC.element_to_be_clickable(
                            (By.CLASS_NAME, "js-overlay-download"))
                    )
                except Exception as e:
                    continue

                # Click the Free Download button
                download_button.click()
                time.sleep(0.2)

                song_metadata = {
                    "title": song_title,
                    "artist": artist,
                    "url": url,
                    "id": id,
                    "description": ""
                }
                # add download thread
                futures.append(executor.submit(download_and_post, download_dir,
                                               song_metadata, wait_time=download_wait_time))

                if len(futures) >= max_threads:
                    while len(futures) > min_threads:
                        futures.popleft().result()
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

        download_song(track_id_list[idx+1:], download_wait_time=download_wait_time,
                      min_threads=min_threads, max_threads=max_threads, process=process)
    finally:
        driver.quit()
        for file in os.listdir(download_dir):
            os.remove(os.path.join(download_dir, file))
        os.rmdir(download_dir)


def download_song_parallel(track_id_list, max_processes=10):
    with ThreadPoolExecutor(max_workers=max_processes) as executor:
        futures = []
        for i in range(0, max_processes):
            start = (i*len(track_id_list))//max_processes
            end = ((i+1)*len(track_id_list))//max_processes
            futures.append(executor.submit(
                download_song, track_id_list[start:end], process=i+1))
        for future in futures:
            future.result()
    DB.save_db()


def main(processes=4, batches=2, max_songs=1000):
    if max_songs is not None:  # randomly select a subset of the tracks
        track_id_list = random.choice(
            list(TRACKS.keys()), max_songs, replace=False)
    else:
        track_id_list = list(TRACKS.keys())

    # Run the download_song feature using this function
    start_time = time.time()
    for i in range(batches):
        print(f"...Downloading batch {i+1} of {batches}...")
        start = (i*len(track_id_list))//batches
        end = ((i+1)*len(track_id_list))//batches
        download_song_parallel(
            track_id_list[start:end], max_processes=processes)
    elapsed_time = time.time() - start_time
    print(f"Elapsed_time: {elapsed_time/60:.2f} minutes")


if __name__ == "__main__":
    main()
