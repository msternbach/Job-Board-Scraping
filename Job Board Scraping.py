#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import time
import datetime
from time import sleep
from random import randint
import re
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


# In[2]:


job_title = []
company_location = []
salary = []
job_description = []
job_links = []


# In[3]:


# Indeed Scraping

chrome_options = Options()
chrome_options.add_argument("--incognito") 
# These configurations are needed to run code using a cron job. Otherwise only argument needed is incognito

chrome_options.add_argument("--headless")
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
chrome_options.add_argument("--no-sandbox")  
chrome_options.add_argument("--disable-dev-shm-usage")  
chrome_options.add_argument("--disable-gpu")  


driver = webdriver.Chrome(options=chrome_options)

# Job terms you want to code to search for on the website
search_terms = ['data+analyst','data+scientist','machine+learning']
for term in search_terms:
    link = 'https://www.indeed.com/jobs?q=' + term + '&l=New+York%2C+NY&sc=0kf%3Aexplvl%28ENTRY_LEVEL%29%3B&radius=15&sort=date&fromage=7&vjk=a4054c4aa537c5b8'
    driver.get(link)

    sleep(randint(3, 5))

    # Cookie button sometimes shows up. Code to click on on it if needed
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[@class="gnav-CookiePrivacyNoticeButton" and @data-gnav-element-name="CookiePrivacyNoticeOk"]'))
        )

        ok_button = driver.find_element(By.XPATH, '//button[@class="gnav-CookiePrivacyNoticeButton" and @data-gnav-element-name="CookiePrivacyNoticeOk"]')
        ok_button.click()
    except:
        pass

    # find how many total listings there are in the search
    total_listings = driver.find_element(By.CLASS_NAME, "jobsearch-JobCountAndSortPane-jobCount").text
    match = re.search(r'\d+', total_listings) # extract number from listings text
    number = int(match.group())
    print(number)
    
    # 15 job listings on each page so this determines how times it needs to loop through to extract all the listings
    if number%15 != 0:
        loop = (number//15) + 1
    else:
        loop = (number//15)
    print(loop)
    # Locate all job listings on the page

    #loop to extract listings
    for i in range(0,loop):
        sleep(randint(3, 5))
        print("loop executed")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "mosaic-jobResults"))
        )
        job_listings = driver.find_elements(By.CLASS_NAME, "job_seen_beacon")

        for job_listing in job_listings:
            # Click on each job listing
            job_listing.click()
            sleep(randint(3, 5))

            try:
                # Wait for the job description element to be present on the page
                description_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="jobDescriptionText"]'))
                )
            except TimeoutException:
                print("Job description not found.")
                
            # for each job listing find title, location, description, salary, and link and append to list
            # Scraper adds "N/A" to list if it can't find element

            try:
                title = job_listing.find_element(By.CLASS_NAME, "jobTitle")
                job_title.append(title.text)
            except NoSuchElementException:
                job_title.append("N/A")

            try:
                location = job_listing.find_element(By.CLASS_NAME, "company_location")
                company_location.append(location.text)
            except NoSuchElementException:
                company_location.append("N/A")

            if 'description_element' in locals():
                description = driver.execute_script("return arguments[0].innerHTML;", description_element)
                job_description.append(description)
            else:
                job_description.append("N/A")

            try:
                # Find the <a> tag with the specific class within the current job listing context
                link_element = job_listing.find_element(By.CSS_SELECTOR, "a.jcs-JobTitle")
                job_link = link_element.get_attribute('href')
                job_links.append(job_link)
            except NoSuchElementException:
                print("Link not found for this job listing.")
                job_links.append("N/A")

            try:
                sal = job_listing.find_element(By.XPATH, "//div[@id='salaryInfoAndJobType']/span[contains(@class, 'css-19j1a75')]")
                salary.append(sal.text)
            except NoSuchElementException:
                salary.append("N/A")

            sleep(randint(3, 5))

        try:
            next_page_button = driver.find_element(By.XPATH, '//a[@data-testid="pagination-page-next"]')

            # Click on the next page button
            next_page_button.click()

            current_url = driver.current_url

            # Wait for the new page to load
            WebDriverWait(driver, 10).until(
                EC.url_changes(current_url)
            )
        except:
            print("Next page button not found")

            
time.sleep(5)

driver.quit()


# In[4]:


print(job_title)
print(company_location)
print(salary)
print(job_description)
print(job_links)


# In[5]:


# Make sure all lists are same length
print(len(job_title))
print(len(company_location))
print(len(salary))
print(len(job_description))
print(len(job_links))


# In[6]:


# Extracts the text from all the elements in the description
description_text = []
for i in job_description:
    soup = BeautifulSoup(i, "html.parser")
    desc = ' '
    ptags = soup.find_all(recursive=False)
    for tag in ptags:
        desc+=tag.get_text()
    description_text.append(desc)


# In[7]:


# Create data array
data = []
data.append(job_title)
data.append(company_location)
data.append(salary)
data.append(description_text)
data.append(job_links)


# In[8]:


# Create a tabular representation of the data
df = pd.DataFrame(np.array(data))

df = df.T

# Add the column names
df.columns = ['job title','location','salary','description','link']

# Print the tabular data
print(df)


# In[9]:


# Get company name and location from location column by spliting the column at first '\n'
df[['company name', 'company location']] = df['location'].str.split('\n', n=1, expand=True)
df.drop(['location'],axis=1,inplace=True)


# In[10]:


# Find any '\n' in dataset and remove it
df = df.replace('\n', '',regex=True)


# In[11]:


df = df[['job title','company name','company location','salary','description','link']]


# In[ ]:


df = df.drop_duplicates(subset=['job title', 'company name'])


# In[ ]:


# Define a ranking function based on job title and description relevance to the user's skills and job preference
def rank_jobs(row):
    # Define keywords and their weights
    keywords = {
        'data analyst': 12,
        'data scientist': 10,
        'business analyst':7,
        'python': 5,
        'sql': 5,
        'tableau': 5,
        'excel': 4,
        'web scraping': 6,
        'machine learning': 5,
        'ai':3,
        'analytics': 3,
        'analysis': 2,
        'mba':10
    }
    
    score = 0
    title = row['job title'].lower()
    description = row['description'].lower()
    
    # Score titles and descriptions based on keyword presence
    for keyword, weight in keywords.items():
        if keyword in title:
            score += weight * 1.5  # Higher weight for title matches
        if keyword in description:
            score += weight
    
    # Additional scoring for preferred location
    if "new york" in row['company location'].lower():
        score += 5  # Slight boost for NYC locations
    
    return score

# Apply ranking to each row
df['relevance_score'] = df.apply(rank_jobs, axis=1)

# Sort the dataframe by the computed relevance score in descending order
ranked_df = df.sort_values(by='relevance_score', ascending=False)

# Display the top 5 ranked jobs to verify the ranking
ranked_df[['job title', 'company name', 'company location', 'relevance_score']].head()


# In[12]:


# Get today's date in the format 'month_day_year'
today = datetime.datetime.now().strftime("%m_%d_%Y")

# Format the filename with today's date
filename = f"indeed_listings_{today}.csv"

# Save the DataFrame to a CSV file with the dynamic filename
df.to_csv(filename)


# In[55]:


df.head(5)


# In[3]:


job_title = []
company_name = []
company_location = []
salary = []
job_description = []
job_links = []


# In[4]:


# Linkedin scraping

chrome_options = Options()
chrome_options.add_argument("--incognito")  # Use Chrome in incognito mode.
# These configurations are needed to run code using a cron job. Otherwise only argument needed is incognito

chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless")
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, necessary on Linux if running as root.
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems.
chrome_options.add_argument("--disable-gpu")  # Applicable to windows os only



driver = webdriver.Chrome(options=chrome_options)

# Use google search first before going straight to linkedin
driver.get("https://google.com")

WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.CLASS_NAME, "gLFyf" )))

input_element = driver.find_element(By.CLASS_NAME, "gLFyf")
input_element.send_keys("linkedin" + Keys.ENTER)

# Code to click on location tracker pop up if it shows up
try:
    location_button = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "Hg3NO"))
        )
        # Click the button
    location_button[1].click()
except:
    pass

# Enter into Linkedin
WebDriverWait(driver, 5).until(
    EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, "linkedin")))

#link.click()
link = driver.find_element(By.PARTIAL_LINK_TEXT, "LinkedIn")
driver.execute_script("arguments[0].click();", link)

sleep(randint(3, 5))

# login to account
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "session_key" )))

username_field = driver.find_element(By.ID, 'session_key')

# Clear any existing text in the field (optional, if needed)
username_field.clear()

# Type your username into the input field
username_field.send_keys('your username')

time.sleep(2)

username_field = driver.find_element(By.ID, 'session_password')

username_field.clear()

# Type your password in
username_field.send_keys('your password')

sign_in_button_xpath = "//button[contains(@class, 'btn-md') and contains(text(), 'Sign in')]"

# Wait for the "Sign in" button to be clickable
sign_in_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, sign_in_button_xpath))
)

# Click the "Sign in" button
sign_in_button.click()

# Wait for a few seconds (optional, adjust as needed)
time.sleep(2)

# Job terms you want to code to search for on the website
search_terms = ['data%20analyst','data%20scientist']

for term in search_terms:
    
    driver.get('https://www.linkedin.com/jobs/search/?currentJobId=3867364542&distance=10&f_E=1%2C2%2C3&f_TPR=r86400&geoId=103004792&keywords=' + term + '&origin=JOB_SEARCH_PAGE_JOB_FILTER&refresh=true')

    time.sleep(2)

    total_listings = driver.find_element(By.CSS_SELECTOR, 'small.display-flex.t-12.t-black--light.t-normal.jobs-search-results-list__text').text

    print(total_listings)

    match = re.search(r'(\d{1,3}(?:,\d{3})*)', total_listings)

    number = int(match.group().replace(',', ''))
    print(number)
    if number%25 != 0:
        loop = (number//25) + 1
    else:
        loop = (number//25)
    print(loop)

    # Locate all job listings on the page

    page = 2

    for i in range(0, loop):
        sleep(randint(3, 5))
        print("loop executed")
        # Section to identify all the listings on page. Some listings won't load if this step isn't done
        for i in range(1, 26):  # Usually 25 listings on each page. If less, look will break early
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__list-container"))
            )
            xpath_expression = '//ul[contains(@class, "scaffold-layout__list-container")]/li[{}]'.format(i)
            sleep(2)
            try:
                WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath_expression)))
                # Process the job_listing as needed
                job_listing = driver.find_element(By.XPATH, xpath_expression)
                # Wait for the new job listings to load
                # Click on each job listing
                job_listing.click()
                sleep(2)
            except (NoSuchElementException, TimeoutException) as e:
                print("listing number", i, "not found") 
                # break loop, no more jobs on this page
                break
        # Loop to actually extract job data
        for i in range(1, 26): 
            print(i)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__list-container"))
            )
            # finds list item for each job on page
            xpath_expression = '//ul[contains(@class, "scaffold-layout__list-container")]/li[{}]'.format(i)
            sleep(2)
            try:
                WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, xpath_expression)))
                # Process the job_listing as needed
                job_listing = driver.find_element(By.XPATH, xpath_expression)
                # Wait for the new job listings to load
                # Click on each job listing
                job_listing.click()
                sleep(randint(3, 5))

                try:
                    # Wait for the job description element to be present on the page
                    title_link = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'job-details-jobs-unified-top-card__job-title')]")
                    ))
                    # Extract the job title from the span element
                    job_title.append(title_link.text)

                except (NoSuchElementException, TimeoutException) as e:
                    # Handle the case where the title link is not found within the given time
                    print(f"Title not found for this job listing due to: {type(e).__name__}")
                    job_title.append("N/A")

                try:
                    div_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "job-details-jobs-unified-top-card__primary-description-without-tagline"))
                    )

                    name_link = div_element.find_element(By.XPATH, "./*[normalize-space(text())][1]")

                    company_name.append(name_link.text)

                except (NoSuchElementException, TimeoutException) as e:
                    # Handle the case where the title link is not found within the given time
                    print(f"Company name not found for this job listing due to: {type(e).__name__}")
                    company_name.append("N/A")

                try:
                    location_element = driver.find_element(By.XPATH, "//div[contains(@class, 'job-details-jobs-unified-top-card__primary-description-without-tagline')]")

                    # Extract the text containing the location
                    location_text = location_element.text

                    # Split the text and get the part containing the location
                    location_parts = location_text.split("·")
                    location = location_parts[1].strip() if len(location_parts) > 1 else "N/A"

                    # Add the location to your list
                    company_location.append(location)

                except NoSuchElementException:
                    print("Location not found for this job listing.")
                    company_location.append("N/A")

                try:
                    # find list element containing salary
                    li_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "li.job-details-jobs-unified-top-card__job-insight"))
                    )

                    # Find first `span` under the parent `span` to get the salary text
                    salary_span = li_element.find_element(By.CSS_SELECTOR, "span > span:nth-of-type(1)")

                    # Extract the Text
                    salary_text = salary_span.text

                    # Add the salary to your list
                    salary.append(salary_text)

                except (NoSuchElementException, TimeoutException) as e:
                    print(f"Salary name not found for this job listing due to: {type(e).__name__}")
                    salary.append("N/A")

                try:
                    description_element = driver.find_element(By.ID, "job-details")

                    job_description.append(description_element.text)

                except NoSuchElementException:
                    print("Description not found for this job listing.")
                    job_description.append("N/A")

                # to extract link for each job
                current_url = driver.current_url
                job_links.append(current_url)

                # Go back to the job listings page
                sleep(5)
            
            # exception handling if listing won't load or no more listing on page
            except (NoSuchElementException, TimeoutException) as e:
                print("listing number", i ,"not found")  
                # no more jobs to scrape on this page
                break
            

        # Locate the "Page 2" button using XPath
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"[aria-label='Page {page}']"))
            )

            page_button = driver.find_element(By.CSS_SELECTOR, f"[aria-label='Page {page}']")

            page+=1

            # Click the "Page 2" button to navigate to the next page
            page_button.click()
        except:
            print("Next page button not found")
        

time.sleep(2)

# Close the browser window
driver.quit()


# In[15]:


print(job_title)
print(company_name)
print(company_location)
print(salary)
print(job_description)
print(job_links)


# In[16]:


# make sure lists all same length
print(len(job_title))
print(len(company_name))
print(len(company_location))
print(len(salary))
print(len(job_description))
print(len(job_links))


# In[17]:


# Create data array
data = []
data.append(job_title)
data.append(company_name)
data.append(company_location)
data.append(salary)
data.append(job_description)
data.append(job_links)


# In[18]:


# Create a tabular representation of the data
df = pd.DataFrame(np.array(data))

df = df.T

# Add the column names
df.columns = ['job title','company name','location','salary','description','link']

# Print the tabular data
print(df)


# In[19]:


# Delete any instances of '\n'
df = df.replace('\n', '',regex=True)


# In[20]:


df = df.drop_duplicates(subset=['job title', 'company name'])


# In[22]:


# Define a ranking function based on job title and description relevance to the user's skills and job preference
def rank_jobs(row):
    # Define keywords and their weights
    keywords = {
        'data analyst': 12,
        'data scientist': 10,
        'business analyst':7,
        'python': 5,
        'sql': 5,
        'tableau': 5,
        'excel': 4,
        'web scraping': 6,
        'machine learning': 5,
        'ai':3,
        'analytics': 3,
        'analysis': 2,
        'mba':10
    }
    
    score = 0
    title = row['job title'].lower()
    description = row['description'].lower()
    
    # Score titles and descriptions based on keyword presence
    for keyword, weight in keywords.items():
        if keyword in title:
            score += weight * 1.5  # Higher weight for title matches
        if keyword in description:
            score += weight
    
    # Additional scoring for preferred location
    if "new york" in row['location'].lower():
        score += 5  # Slight boost for NYC locations
    
    return score

# Apply ranking to each row
df['relevance_score'] = df.apply(rank_jobs, axis=1)

# Sort the dataframe by the computed relevance score in descending order
ranked_df = df.sort_values(by='relevance_score', ascending=False)

# Display the top 5 ranked jobs to verify the ranking
ranked_df[['job title', 'company name', 'location', 'relevance_score']].head()


# In[23]:


# Get today's date in the format 'month_day_year'
today = datetime.datetime.now().strftime("%m_%d_%Y")

# Format the filename with today's date
filename = f"linkedin_listings_{today}.csv"

# Save the DataFrame to a CSV file with the dynamic filename
ranked_df.to_csv(filename)


# In[6]:


# Need to import to handle google 2 step authentication in login process
import pyotp

# pyotp.totp.TOTP('secret_key').provisioning_uri(name='your_account', issuer_name='service name')
pyotp.totp.TOTP('XEI2ZAAZB7LDMIBSGGTHXQBOLH2ZZ7QR').provisioning_uri(name='msternb2@binghamton.edu', issuer_name='binghamton.edu')


# In[7]:


# use otpauth above
authen = pyotp.parse_uri('otpauth://totp/binghamton.edu:msternb2%40binghamton.edu?secret=XEI2ZAAZB7LDMIBSGGTHXQBOLH2ZZ7QR&issuer=binghamton.edu')
print(authen.now())


# In[8]:


job_title = []
company_name = []
location_name = []
salary = []
job_description = []


# In[9]:


# handshake scraping

chrome_options = Options()
chrome_options.add_argument("--incognito")  # Use Chrome in incognito mode.
# These configurations are needed to run code using a cron job. Otherwise only argument needed is incognito
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--headless")
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36')
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, necessary on Linux if running as root.
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems.
chrome_options.add_argument("--disable-gpu")  # Applicable to windows os only


driver = webdriver.Chrome(options=chrome_options)

# Go to handshake website
driver.get("https://app.joinhandshake.com/stu/postings?page=1&per_page=25&sort_direction=desc&sort_column=created_at&locations%5B%5D%5Blabel%5D=New%20York%2C%20NY&locations%5B%5D%5Bname%5D=New%20York%2C%20NY&locations%5B%5D%5Bdistance%5D=15mi&locations%5B%5D%5Bpoint%5D=40.7534164%2C%20-73.9911957&locations%5B%5D%5Blatitude%5D=40.7534164&locations%5B%5D%5Blongitude%5D=-73.9911957&query=data%20scientist")
sleep(randint(3, 5))

# Access school dropdown
dropdown_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "select2-choice.select2-default"))
    )
dropdown_link.click()

# Find school input textbox
WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "s2id_autogen1_search"))
    )

school_field = driver.find_element(By.ID, "s2id_autogen1_search")

school_field.clear()

# Put in your school
school_field.send_keys('Binghamton')

time.sleep(2)

school_field.send_keys(Keys.ARROW_DOWN)

school_field.send_keys(Keys.ENTER)

signin_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "sso-name")))
signin_link.click()
    
WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    
username = driver.find_element(By.ID, "username")

username.clear()

# type your username
username.send_keys('your username')
    
password = driver.find_element(By.ID, "password")

password.clear()

# type your password
password.send_keys('your password')
  
password.send_keys(Keys.ENTER)

WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "token"))
    )
    
token = driver.find_element(By.ID, "token")

token.clear()

# Put in google authentication you set up in previous step
token.send_keys(authen.now())
        
token.send_keys(Keys.ENTER)

time.sleep(2)

# Job terms you want code to search for on the website
search_terms = ['data%20analyst','data%20scientist','analytics']

for term in search_terms:
    print(term)
    page = 1
    more_pages = True

    # Keeps going until no more new postings
    while more_pages:
        print('loop_executed')
        # Navigate to the URL with the current page number
        driver.get('https://app.joinhandshake.com/stu/postings?page='+ str(page) +'&per_page=25&sort_direction=desc&sort_column=created_at&locations%5B%5D%5Blabel%5D=New%20York%2C%20NY&locations%5B%5D%5Bname%5D=New%20York%2C%20NY&locations%5B%5D%5Bdistance%5D=15mi&locations%5B%5D%5Bpoint%5D=40.7534164%2C%20-73.9911957&locations%5B%5D%5Blatitude%5D=40.7534164&locations%5B%5D%5Blongitude%5D=-73.9911957&query=' + term)
        sleep(randint(3, 5))
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "style__cards-container___IClnP"))
        )

        job_listings = driver.find_elements(By.CLASS_NAME, "style__card___XOQvr")

        fresh_found = False
    
        for job_listing in job_listings:
            try:
                # Locate the parent div based on its structure and the presence of a <p> tag with text ending in 'ago'
                parent_div = job_listing.find_element(By.XPATH, ".//div[contains(@class, 'sc-') and .//p[contains(text(), 'ago')]]")
                # Find the first <p> element within this parent <div>
                first_p_element = parent_div.find_element(By.XPATH, ".//p[contains(@class, 'sc-')]")
                if 'month' in first_p_element.text:
                    more_pages = False
                    break
            except NoSuchElementException:
                continue  # Continue 

            fresh_found = True
            
            # Wait for the new job listings to load
            # Click on each job listing
            job_listing.click()
            sleep(randint(3, 5))

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="skip-to-content"]/div[4]/div/div[1]/div/div/form/div[2]/div/div/div[2]/div[1]/a/h1'))
                )
                title_link = driver.find_element(By.XPATH, '//*[@id="skip-to-content"]/div[4]/div/div[1]/div/div/form/div[2]/div/div/div[2]/div[1]/a/h1')
                job_title.append(title_link.text)
                print(title_link.text)

            except (NoSuchElementException, TimeoutException) as e:
                # Handle the case where the title link is not found within the given time
                print(f"Title not found for this job listing due to: {type(e).__name__}")
                job_title.append("N/A")

            try:
                # Adjusting for 'company_name'
                name_link = driver.find_element(By.XPATH, '//*[@id="skip-to-content"]/div[4]/div/div[1]/div/div/form/div[2]/div/div/div[2]/div[1]/div[1]/div/a[1]/div')
                company_name.append(name_link.text)

            except NoSuchElementException:
                # Handle the case where the link is not found
                print("Company name not found for this job listing.")
                company_name.append("N/A")
                
            try:
                location_link = driver.find_element(By.XPATH, '//*[@id="skip-to-content"]/div[4]/div/div[1]/div/div/form/div[2]/div/div/div[2]/div[1]/div[3]/div[3]/div[2]/div/div[1]')
                location_name.append(location_link.text)

            except NoSuchElementException:
                # Handle the case where the link is not found
                print("Location not found for this job listing.")
                location_name.append("N/A")

                    # Adjusting for 'salary'
            try:
                salary_element = driver.find_element(By.XPATH, '//*[@id="skip-to-content"]/div[4]/div/div[1]/div/div/form/div[2]/div/div/div[2]/div[1]/div[3]/div[3]/div[1]/div/div[1]')
                salary.append(salary_element.text)  # Ensure 'salary' is the correct list variable for appending

            except NoSuchElementException:
                print("Salary not found for this job listing.")
                salary.append("N/A")
                
            try:
                more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'More')]"))
                )
                more_button.click()  # Click the "More" button to expand the job description
            except TimeoutException:
                print("No 'More' button found or it was not clickable.")

            try:
                # Adjusting for 'job_description'
                description_element = driver.find_element(By.XPATH, '//*[@id="skip-to-content"]/div[4]/div/div[1]/div/div/form/div[2]/div/div/div[2]/div[1]/div[3]/div[4]/div/div/div')
                job_description.append(description_element.text)
            except NoSuchElementException:
                print("Description not found for this job listing.")
                job_description.append("N/A")
        # Go back to the job listings page
        sleep(randint(3, 5))

            # Locate the "Page 2" button using CSS Selector
            # Adjust the CSS Selector if needed to accurately select the "Page 2" button
        if fresh_found and more_pages:
                # Check for the presence of a "Next" page button and try to click it if possible
                try:
                    next_page_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-hook='search-pagination-next']"))
                    )
                    next_page_button.click()
                    page += 1  # Prepare for the next page in the next iteration
                    sleep(randint(3, 5))  # Wait for the page to load properly
                except (NoSuchElementException, TimeoutException):
                    print("Reached the last page for the current search term.")
                    more_pages = False
        else:
            # If no fresh markers were found or there are no more pages, then stop looking through pages
            break
        

        

# Wait for a few seconds (optional, adjust as needed)
time.sleep(2)

# Perform any additional actions or move on to the next step

# Close the browser window
driver.quit()


# In[10]:


print(job_title)
print(company_name)
print(location_name)
print(salary)
print(job_description)


# In[11]:


# make sure all lists the same length
print(len(job_title))
print(len(company_name))
print(len(location_name))
print(len(salary))
print(len(job_description))


# In[ ]:





# In[ ]:





# In[12]:


data = []
data.append(job_title)
data.append(company_name)
data.append(location_name)
data.append(salary)
data.append(job_description)


# In[13]:


print(data)


# In[14]:


df = pd.DataFrame(np.array(data))

df = df.T

# Add the column names
df.columns = ['job title','company','location','salary','description']

# Print the tabular data
print(df)


# In[15]:


# Get ride all instances of '\n' in the data
df = df.replace('\n', '',regex=True)


# In[17]:


df = df.drop_duplicates(subset=['job title', 'company'])


# In[19]:


# Define a ranking function based on job title and description relevance to the user's skills and job preference
def rank_jobs(row):
    # Define keywords and their weights
    keywords = {
        'data analyst': 12,
        'data scientist': 10,
        'business analyst':7,
        'python': 5,
        'sql': 5,
        'tableau': 5,
        'excel': 4,
        'web scraping': 6,
        'machine learning': 5,
        'ai':3,
        'analytics': 3,
        'analysis': 2,
        'mba':10
    }
    
    score = 0
    title = row['job title'].lower()
    description = row['description'].lower()
    
    # Score titles and descriptions based on keyword presence
    for keyword, weight in keywords.items():
        if keyword in title:
            score += weight * 1.5  # Higher weight for title matches
        if keyword in description:
            score += weight
    
    # Additional scoring for preferred location
    if "new york" in row['location'].lower():
        score += 5  # Slight boost for NYC locations
    
    return score

# Apply ranking to each row
df['relevance_score'] = df.apply(rank_jobs, axis=1)

# Sort the dataframe by the computed relevance score in descending order
ranked_df = df.sort_values(by='relevance_score', ascending=False)

# Display the top 5 ranked jobs to verify the ranking
ranked_df[['job title', 'company', 'location', 'relevance_score']].head()


# In[20]:


# Get today's date in the format 'month_day_year'
today = datetime.datetime.now().strftime("%m_%d_%Y")

# Format the filename with today's date
filename = f"handshake_listings_{today}.csv"

# Save the DataFrame to a CSV file with the dynamic filename
df.to_csv(filename)


# In[ ]:




