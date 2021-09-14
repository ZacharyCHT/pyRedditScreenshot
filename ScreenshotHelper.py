import ssl
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import os
import time
from datetime import datetime
import requests
import json
from config import imgbb_api_key, mongodb_pass
import pymongo
from pytz import timezone


class Screenshotter:
    def __init__(self):
        self.geckodriver_path = os.path.abspath(os.path.join(r'geckodriver\geckodriver.exe'))
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        self.output_path = os.path.join(self.project_root, "pictures")
        self.reddit_url = "http://old.reddit.com/r/"
        self.options = Options()
        self.options.headless = True
        self.driver = webdriver.Firefox(
            options=self.options,
            executable_path=self.geckodriver_path,
        )
        self.imgbb_url = 'https://api.imgbb.com/1/upload'
        self.client = pymongo.MongoClient(
            f"mongodb+srv://dbUser:{mongodb_pass}@cluster0.nv3se.mongodb.net/RedditScreenshots?retryWrites=true&w=majority",
            ssl=True,
            ssl_cert_reqs=ssl.CERT_NONE,
        )
        self.db = self.client['RedditScreenshots']
        self.collection = self.db['noidea']

    # List databases for testing
    def list_database(self):
        for db in self.client.list_databases():
            print(db)

    # This function returns file name for the screenshot to be named later
    def get_filename(self, subreddit):
        filename = r"{}-{}".format(subreddit, time.strftime("%Y-%m-%d-%H-%M-%S"))
        return filename

    # This function takes a screenshot as base64 and uploads it to imgbb then makes an entry in the database with other data
    #
    #
    # clean this function up and possibly multifurcate it until it is clean looking
    #
    #
    def take_screenshot(self, subreddit_list):
        for subreddit in subreddit_list:
            self.driver.get(self.reddit_url+subreddit)
            temp = self.driver.find_elements_by_css_selector('span.number')
            # Metadata
            subscribers = temp[0].text
            active = temp[1].text
            # Diagnostic
            print("Subreddit: {} has {} subscribers, and {} active users. Screenshotting the subreddit now.".format(subreddit, subscribers, active))
            content = self.driver.find_element_by_css_selector('body')
            screenshot = content.screenshot_as_base64
            payload = {
                "key": imgbb_api_key,
                "image": screenshot,
                "name": self.get_filename(subreddit)
            }
            res = requests.post(self.imgbb_url, payload)
            response_obj = json.loads(res.text)
            #print(json.dumps(json.loads(res.text), indent=2))
            info = {
                "ss_link": response_obj["data"]["display_url"],
                "subreddit": subreddit,
                "subscribers": int(subscribers.replace(',', '')),
                "active": int(active.replace(',', '')),
                "timestamp": datetime.strptime(datetime.now(tz=timezone('US/Eastern')).strftime('%m/%d/%Y %I:%M:%S'), '%m/%d/%Y %H:%M:%S'),
                "epoch": time.time(),
                "base64": screenshot,
            }
            #print(info)
            self.collection.insert(info)

# This script shouldn't be the first script in the execution sequence
if __name__ == "__main__":
    raise RuntimeError("Screenshotter module should not be run by itself, run main.py instead.")
