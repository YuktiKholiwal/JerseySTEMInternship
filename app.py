import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import csv

# Initialize Options to start Chrome as headless in selenium
chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--headless")

# Initialize the chrome webdriver as 'browser'
browser = webdriver.Chrome(options=chrome_options)
# Get the login page for linkedin
browser.get('https://www.linkedin.com/login')

title = browser.title
# Open the file with the username and password for LinkedIn login
username = "your linkedin email"
password = "your linkedin password"

# Username and Password for login
elementID = browser.find_element(by=By.ID,value='username')
elementID.send_keys(username)

elementID = browser.find_element(by=By.ID,value='password')
elementID.send_keys(password)

elementID.submit()
time.sleep(5)
#enter the link of the post you want to extract the information for
link = "https://www.linkedin.com/posts/jerseystem_jerseystem-genealogydna-ancestryresearch-activity-7172252296926388227-Nsc4?utm_source=share&utm_medium=member_desktop"
browser.get(link)

# pause before scrolling
SCROLL_PAUSE_TIME = 6

# Get the scroll height of the page
last_height = browser.execute_script("return document.body.scrollHeight")

# scroll the entire page due to dynamic loading of the webpage we need to load the entire webpage by scrolling
for i in range(3):
    # Scroll down to bottom
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
    time.sleep(SCROLL_PAUSE_TIME / 2)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight*(2/3));")
    time.sleep(SCROLL_PAUSE_TIME / 2)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = browser.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# use beautiful soup for html parsing
src = browser.page_source
soup = BeautifulSoup(src, 'lxml')

# BASIC INFO LIST

likes_element = soup.find('button', {'class': 't-black--light display-flex align-items-center social-details-social-counts__count-value social-details-social-counts__count-value-hover t-12 hoverable-link-text'})  # This class name is an example; you need to update it
repost_element = soup.find('button', {'class': 'ember-view t-black--light social-details-social-counts__count-value-hover t-12 hoverable-link-text'})
comment_element = soup.find('button', {'class': 't-black--light social-details-social-counts__count-value social-details-social-counts__count-value-hover t-12 hoverable-link-text'})
# Extract the likes count
if likes_element:
    likes_count = likes_element.text.strip()
    print("Likes count:", likes_count)
else:
    print("Likes element not found")

likes_button = browser.find_element(By.CSS_SELECTOR, 'button.social-details-social-counts__count-value')
likes_button.click()


time.sleep(SCROLL_PAUSE_TIME)

updated_src = browser.page_source
soup = BeautifulSoup(updated_src, 'lxml')
names = soup.find_all('div', {'class': 'scaffold-finite-scroll__content'})  # Update with actual class names or identifiers
likers = browser.find_elements(By.CSS_SELECTOR, 'div.artdeco-entity-lockup__title.ember-view')
degrees = browser.find_elements(By.CSS_SELECTOR,'span.artdeco-entity-lockup__degree')
titles= browser.find_elements(By.CSS_SELECTOR,'div.artdeco-entity-lockup__caption.ember-view')


data = []

likers_anchors = browser.find_elements(By.CSS_SELECTOR, 'a.link-without-hover-state.ember-view')
# Assuming likers, degrees, and titles are lists of web elements fetched correctly and have equal lengths
for i in range(len(degrees)):
    name = likers[i].text.strip()
    degree = degrees[i].text.strip() if i < len(degrees) else ''
    title = titles[i].text.strip() if i < len(titles) else ''
    href = likers_anchors[i].get_attribute('href') if i < len(likers_anchors) else 'No Link'
    data.append({
        'Name': name,
        'Degree': degree,
        'Title': title,
        'Profile Link': href,
        'Type of Engagement': 'Like'
    })

# Now, write the data to a CSV file


close_button = browser.find_element(By.CSS_SELECTOR, 'button.artdeco-button.artdeco-button--circle.artdeco-button--muted.artdeco-button--2.artdeco-button--tertiary.ember-view.artdeco-modal__dismiss')
close_button.click()

if repost_element:
    repost_count = repost_element.text.strip()
    print("Repost count:", repost_count)
else:
    print("Repost not found")

if comment_element:
    comment_count = comment_element.text.strip()
    print("Comment count:", comment_count)
else:
    print("Comment not found")
#repost_button = browser.find_element(By.CSS_SELECTOR, 'li.social-details-social-counts__item.social-details-social-counts__item--right-aligned')
#repost_button.click()

commenters = browser.find_elements(By.CSS_SELECTOR, 'span.comments-post-meta__name-text.hoverable-link-text.mr1')
comment_degrees = browser.find_elements(By.CSS_SELECTOR,'span.mr1.t-normal.t-black--light')
comment_titles= browser.find_elements(By.CSS_SELECTOR,'span.comments-post-meta__headline.t-12.t-normal.t-black--light')
commenters_anchors = browser.find_elements(By.CSS_SELECTOR, 'a.app-aware-link.inline-flex.overflow-hidden.t-16.t-black.t-bold.tap-target')

for i in range(len(commenters)):
    name = commenters[i].text.strip()
    degree = comment_degrees[i].text.strip() if i < len(comment_degrees) else ''
    title = comment_titles[i].text.strip() if i < len(comment_titles) else ''
    href = commenters_anchors[i].get_attribute('href') if i < len(commenters_anchors) else 'No Link'
    data.append({
        'Name': name,
        'Degree': degree,
        'Title': title,
        'Profile Link': href,
        'Type of Engagement': 'Comment'
    })

csv_file_path = 'info.csv' #name of the csv file which will get the information
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Name', 'Degree', 'Title', 'Profile Link', 'Type of Engagement'])
    writer.writeheader()
    for row in data:
        writer.writerow(row)

print(f'Data written to {csv_file_path}')