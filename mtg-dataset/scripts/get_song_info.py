from commons import read_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import traceback

input_file = '../data/autotagging.tsv'
tracks, tags, extra = read_file(input_file)

print("Tracks:", tracks)

print("---------------------------------")

# Lets only save a few track ids so that we can start web scrapping
def get_track_ids(tracks):
    return list(tracks.keys())

track_ids = get_track_ids(tracks)
print("Tracks without info:", track_ids)

def download_song (track_id, email, password):

    # Define the url to the track_id
    url = "https://www.jamendo.com/track/" + str(track_id)

    driver = webdriver.Chrome()

    try:
        driver.get("https://www.jamendo.com/start")
        login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Log in')]"))
        )
        login_button.click()
        print("LOG IN button clicked!")

        # Wait for the login window to appear
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@name='email']"))
        )

        # Find the email and password fields, find the log in button
        email_field = driver.find_element(By.XPATH, "//input[@name='email']") 
        password_field = driver.find_element(By.XPATH, "//input[@name='password']") 
        submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]") 

        # Enter you log in info
        email_field.send_keys(email)
        password_field.send_keys(password) 

        # Locate the log in button
        submit_button = driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'btn btn--brand btn--lg js-signin-form')]")

        # Use Javascript to click the log in button
        print("Click the log in button")
        driver.execute_script("arguments[0].click();", submit_button)

        # Wait a bit to make sure that you are logged in
        time.sleep(5)
        print("Login completed!")
        print("Logged in successfully!")

        driver.get(url)

        # Wait for the Download button to load
        print("Waiting for the Download button")
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "js-abtesting-trigger-start"))
        )

        # Click the Download button
        print("Clicking the download button")
        download_button.click()
        print("Download button clicked")

        # Wait for the download button to load
        print("Waiting for the free download button to load")
        download_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "js-overlay-download"))
        )

        # Click the Free Download button
        print("Clicking the free download button")
        download_button.click()
        print("Free download button clicked")

        time.sleep(5)

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()

# TO USE THE ABOVE FUNCTION:

# First, specify a track id
first_track_id = track_ids[0]
first_track = tracks[first_track_id]

# Then, define an email and password!
email = "EMAIL"
password = "PASSWORD"

# Run the download_song feature using this function
download_song(first_track_id, email, password)