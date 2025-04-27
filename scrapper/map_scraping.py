import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import re
import json


def setup_driver():
    """Set up and return a Chrome webdriver with appropriate options."""
    options = Options()
    # Uncomment the line below if you want to run in headless mode
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=en-US")  # Force English language
    options.add_argument("--accept-lang=en-US,en;q=0.9")
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

    # Initialize the Chrome driver
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.google.com")
    driver.add_cookie({"name": "PREF", "value": "hl=en"})
    return driver

def extract_coordinates(driver):
    """Extract latitude and longitude from the Google Maps page."""
    try:
        print("Trying to extract coordinates...")
        coordinates = {"latitude": None, "longitude": None}
        
        # Method 1: Extract from URL
        current_url = driver.current_url
        print(f"Current URL: {current_url}")
        
        # Look for @<lat>,<lng> pattern in URL
        url_pattern = r'@(-?\d+\.\d+),(-?\d+\.\d+)'
        url_match = re.search(url_pattern, current_url)
        if url_match:
            coordinates["latitude"] = url_match.group(1)
            coordinates["longitude"] = url_match.group(2)
            print(f"Extracted coordinates from URL: {coordinates['latitude']}, {coordinates['longitude']}")
            return coordinates
        
        # Method 2: Extract from page metadata
        try:
            # Look for JSON-LD script tags that might contain coordinates
            script_elements = driver.find_elements(By.TAG_NAME, "script")
            for script in script_elements:
                script_content = script.get_attribute("innerHTML")
                if "latitude" in script_content and "longitude" in script_content:
                    # Try to parse JSON content
                    try:
                        # Find JSON blocks in the script
                        json_match = re.search(r'({[^{}]*"latitude"[^{}]*})', script_content)
                        if json_match:
                            json_data = json.loads(json_match.group(1))
                            if "latitude" in json_data and "longitude" in json_data:
                                coordinates["latitude"] = str(json_data["latitude"])
                                coordinates["longitude"] = str(json_data["longitude"])
                                print(f"Extracted coordinates from metadata: {coordinates['latitude']}, {coordinates['longitude']}")
                                return coordinates
                    except:
                        pass
        except Exception as e:
            print(f"Error extracting coordinates from metadata: {e}")
        
        # Method 3: Try to extract from share URL/button
        try:
            # Click on share button if it exists
            share_button_selectors = [
                'button[aria-label*="Share"]',
                'button[jsaction*="share"]',
                'button[data-value="Share"]'
            ]
            
            for selector in share_button_selectors:
                try:
                    share_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                    if share_buttons:
                        for button in share_buttons:
                            if button.is_displayed():
                                print("Found share button, clicking...")
                                driver.execute_script("arguments[0].click();", button)
                                time.sleep(2)
                                
                                # Try to find URL input in share dialog
                                url_input_selectors = [
                                    'input[aria-label*="Copy link"]',
                                    'input.vrsrZe'
                                ]
                                
                                for input_selector in url_input_selectors:
                                    try:
                                        url_inputs = driver.find_elements(By.CSS_SELECTOR, input_selector)
                                        if url_inputs:
                                            share_url = url_inputs[0].get_attribute("value")
                                            print(f"Share URL: {share_url}")
                                            
                                            # Extract coordinates from share URL
                                            url_match = re.search(url_pattern, share_url)
                                            if url_match:
                                                coordinates["latitude"] = url_match.group(1)
                                                coordinates["longitude"] = url_match.group(2)
                                                print(f"Extracted coordinates from share URL: {coordinates['latitude']}, {coordinates['longitude']}")
                                                
                                                # Close share dialog
                                                try:
                                                    close_buttons = driver.find_elements(By.CSS_SELECTOR, 'button[aria-label="Close"]')
                                                    if close_buttons:
                                                        driver.execute_script("arguments[0].click();", close_buttons[0])
                                                        time.sleep(1)
                                                except:
                                                    pass
                                                
                                                return coordinates
                                    except:
                                        continue
                except:
                    continue
        except Exception as e:
            print(f"Error extracting coordinates from share button: {e}")
        
        # Method 4: Extract from page source
        try:
            page_source = driver.page_source
            # Look for coordinates in raw HTML
            coord_pattern = r'"latitude":(-?\d+\.\d+),"longitude":(-?\d+\.\d+)'
            coord_match = re.search(coord_pattern, page_source)
            if coord_match:
                coordinates["latitude"] = coord_match.group(1)
                coordinates["longitude"] = coord_match.group(2)
                print(f"Extracted coordinates from page source: {coordinates['latitude']}, {coordinates['longitude']}")
                return coordinates
        except Exception as e:
            print(f"Error extracting coordinates from page source: {e}")
            
        print("Could not extract coordinates using any method")
        return coordinates
        
    except Exception as e:
        print(f"Error extracting coordinates: {e}")
        return {"latitude": None, "longitude": None}

def find_first_business_and_click(driver):
    """Find and click on the first business result."""
    try:
        print("Looking for the first business result...")
        # Wait for search results to load
        time.sleep(5)
        
        # Try multiple selectors for business listings
        business_selectors = [
            'a[href*="maps/place"]',
            'div[role="article"]',
            'div.V0h1Ob-haAclf',
            'div.Nv2PK'
        ]
        
        for selector in business_selectors:
            try:
                businesses = driver.find_elements(By.CSS_SELECTOR, selector)
                if businesses:
                    print(f"Found {len(businesses)} businesses with selector: {selector}")
                    # Click on the first result
                    businesses[0].click()
                    print("Clicked on the first business")
                    time.sleep(3)
                    return True
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
                
        print("Could not find any business listings")
        return False
        
    except Exception as e:
        print(f"Error finding first business: {e}")
        return False

def click_reviews_tab(driver):
    """Find and click on the reviews tab."""
    try:
        print("Attempting to click on reviews tab...")
        time.sleep(5)
        
        # First try to find reviews tab by text content
        try:
            # Try using JavaScript to find and click the reviews tab by text content
            js_script = """
            var elements = document.querySelectorAll('button, div[role="tab"]');
            for (var i = 0; i < elements.length; i++) {
                if (elements[i].textContent.toLowerCase().includes('review')  || 
                    elements[i].textContent.includes('クチコミ')){
                    elements[i].click();
                    return true;
                }
            }
            return false;
            """
            clicked = driver.execute_script(js_script)
            if clicked:
                print("Successfully clicked reviews tab using JavaScript")
                time.sleep(3)
                return True
        except Exception as e:
            print(f"JavaScript approach failed: {e}")
        
        # If JavaScript approach failed, try more specific methods
        review_tab_selectors = [
            'button[aria-label*="review"]',
            'button[data-tab*="review"]',
            'div[role="tab"][aria-label*="review"]',
            'button[jsaction*="reviewsAction"]',
            'button.hh2c6',  # Common class for tabs
            '[role="tab"]:nth-child(2)'  # Reviews are often the second tab
        ]
        
        for selector in review_tab_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        # Check if this element contains "review" text
                        if "review" in element.text.lower():
                            print(f"Found reviews tab with selector: {selector}")
                            driver.execute_script("arguments[0].click();", element)
                            print("Clicked on reviews tab")
                            time.sleep(3)
                            return True
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
                
        print("Could not find reviews tab")
        return False
        
    except Exception as e:
        print(f"Error clicking reviews tab: {e}")
        return False

def scroll_reviews(driver, scrolls=10, scroll_pause=1.5):
    """Scroll down the reviews section to load more reviews."""
    try:
        print("Starting to scroll through reviews...")
        
        # Try to find the scrollable container
        scroll_container_selectors = [
            'div[role="feed"]',
            'div.m6QErb[aria-label*="review"]',
            'div.m6QErb.DxyBCb.kA9KIf',
            'div[aria-label*="review"][role="region"]',
            'div.m6QErb',  # General container class
            'div.DxyBCb.kA9KIf'  # Another common container class
        ]
        
        scroll_container = None
        for selector in scroll_container_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    for element in elements:
                        # Check if this element contains review elements
                        child_reviews = element.find_elements(By.CSS_SELECTOR, 'div.jftiEf, div[data-review-id]')
                        if child_reviews:
                            scroll_container = element
                            print(f"Found scroll container with selector: {selector}")
                            break
                if scroll_container:
                    break
            except Exception as e:
                print(f"Error finding scroll container with selector {selector}: {e}")
                continue
        
        if not scroll_container:
            print("Could not find scroll container, trying to use body element")
            scroll_container = driver.find_element(By.TAG_NAME, 'body')
        
        # Scroll using multiple methods
        for i in range(scrolls):
            print(f"Scrolling {i+1}/{scrolls}...")
            
            # Method 1: JavaScript scroll
            try:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
            except:
                pass
                
            # Method 2: Send Page Down key to the container
            try:
                scroll_container.send_keys(Keys.PAGE_DOWN)
            except:
                pass
                
            # Method 3: Use ActionChains to scroll
            try:
                ActionChains(driver).move_to_element(scroll_container).send_keys(Keys.PAGE_DOWN).perform()
            except:
                pass
                
            # Method 4: JavaScript scroll in viewport
            try:
                driver.execute_script("arguments[0].scrollIntoView(false);", scroll_container)
            except:
                pass
            
            time.sleep(scroll_pause)
            
    except Exception as e:
        print(f"Error while scrolling: {e}")

def expand_all_reviews(driver):
    """Find and click all 'More' buttons to expand review text."""
    try:
        print("Attempting to expand all reviews...")
        
        # Try different selectors for "More" buttons
        more_button_selectors = [
            'button[aria-label="More"]',
            'button.w8nwRe',
            'button.ysrH9e',
            'button[jsaction*="expand"]'
        ]
        
        total_clicked = 0
        for selector in more_button_selectors:
            try:
                more_buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                if more_buttons:
                    print(f"Found {len(more_buttons)} 'More' buttons with selector: {selector}")
                    for button in more_buttons:
                        try:
                            if button.is_displayed():
                                driver.execute_script("arguments[0].click();", button)
                                total_clicked += 1
                                time.sleep(0.2)
                        except:
                            continue
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
                
        print(f"Expanded {total_clicked} reviews")
        
    except Exception as e:
        print(f"Error expanding reviews: {e}")

def extract_place_info(driver):
    """Extract basic information about the place."""
    place_info = {
        "name": "Unknown",
        "address": "Unknown",
        "phone": "Unknown",
        "website": "Unknown",
        "rating": "Unknown",
        "total_reviews": "Unknown",
        "categories": "Unknown"
    }
    
    try:
        print("Extracting place information...")
        
        # Extract name
        name_selectors = [
            'h1.DUwDvf',
            'h1.fontHeadlineLarge',
            'div.P5Bobd'
        ]
        
        for selector in name_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    place_info["name"] = elements[0].text
                    print(f"Found place name: {place_info['name']}")
                    break
            except:
                continue
        
        # Extract address
        address_selectors = [
            'button[data-item-id="address"]',
            'span.desktop-more-info-widget-place-address'
        ]
        
        for selector in address_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    place_info["address"] = elements[0].text
                    print(f"Found address: {place_info['address']}")
                    break
            except:
                continue
        
        # Extract phone number
        phone_selectors = [
            'button[data-item-id*="phone"]',
            'span.QSFF4-text'
        ]
        
        for selector in phone_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    place_info["phone"] = elements[0].text
                    print(f"Found phone: {place_info['phone']}")
                    break
            except:
                continue
        
        # Extract website
        website_selectors = [
            'a[data-item-id*="authority"]',
            'a[jsaction*="website"]'
        ]
        
        for selector in website_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    place_info["website"] = elements[0].get_attribute("href")
                    print(f"Found website: {place_info['website']}")
                    break
            except:
                continue
        
        # Extract rating
        rating_selectors = [
            'div.F7nice',
            'span.ceNzKf',
            'span.rW3L9c'
        ]
        
        for selector in rating_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    place_info["rating"] = elements[0].text
                    print(f"Found rating: {place_info['rating']}")
                    break
            except:
                continue
        
        # Extract total reviews
        reviews_count_selectors = [
            'span.F7nice',
            'span.r-i7DoTkIFmMnw',
            'span.DkEaL'
        ]
        
        for selector in reviews_count_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Try to extract just the number
                    text = elements[0].text
                    match = re.search(r'(\d+(?:,\d+)*)', text)
                    if match:
                        place_info["total_reviews"] = match.group(1)
                    else:
                        place_info["total_reviews"] = text
                    print(f"Found total reviews: {place_info['total_reviews']}")
                    break
            except:
                continue
        
        # Extract categories
        category_selectors = [
            'div.Io6YTe',
            'span.YhemCb',
            'button[jsaction*="category"]'
        ]
        
        for selector in category_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    place_info["categories"] = elements[0].text
                    print(f"Found categories: {place_info['categories']}")
                    break
            except:
                continue
                
        return place_info
        
    except Exception as e:
        print(f"Error extracting place info: {e}")
        return place_info

def extract_reviews(driver):
    """Extract reviews from the Google Maps page."""
    reviews = []
    
    try:
        print("Extracting reviews...")
        
        # Potential selectors for review elements
        review_element_selectors = [
            'div[data-review-id]',
            'div.jftiEf',
            'div.gws-localreviews__google-review'
        ]
        
        review_elements = []
        for selector in review_element_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    review_elements = elements
                    print(f"Found {len(elements)} reviews with selector '{selector}'")
                    break
            except:
                continue
        
        if not review_elements:
            print("No review elements found.")
            return reviews
            
        # Process each review
        for i, review in enumerate(review_elements):
            try:
                print(f"Processing review {i+1}/{len(review_elements)}")
                
                # Extract reviewer name - try different selectors
                name = "Unknown"
                name_selectors = [
                    'div.d4r55',
                    'div.TSUbDb',
                    'span.x3AX1-LfntMc-header-title-title',
                    'a.DHIhE',
                    'div.Tfgpc'
                ]
                for selector in name_selectors:
                    try:
                        name_elements = review.find_elements(By.CSS_SELECTOR, selector)
                        if name_elements:
                            name = name_elements[0].text
                            if name:
                                print(f"Found name: {name}")
                                break
                    except:
                        continue
                
                # Extract rating - try different approaches
                rating = "N/A"
                try:
                    # Method 1: Look for rating in aria-label attribute
                    rating_elements = review.find_elements(By.CSS_SELECTOR, 'span[role="img"]')
                    for element in rating_elements:
                        rating_text = element.get_attribute('aria-label')
                        if rating_text:
                            rating_match = re.search(r'(\d+)', rating_text)
                            if rating_match:
                                rating = rating_match.group(1)
                                print(f"Found rating: {rating}")
                                break
                except:
                    try:
                        # Method 2: Count filled stars
                        stars = review.find_elements(By.CSS_SELECTOR, 'img[src*="star_"]')
                        if stars:
                            filled_stars = [s for s in stars if 'star_fill' in s.get_attribute('src')]
                            rating = str(len(filled_stars))
                            print(f"Found rating by counting stars: {rating}")
                    except:
                        pass
                
                # Extract review text - try multiple selectors
                review_text = ""
                text_selectors = [
                    'span[class*="fontBodyMedium"]',
                    'span.wiI7pd',
                    'div.MyEned',
                    'span.review-full-text',
                    'div.Jtu6Td'
                ]
                
                for selector in text_selectors:
                    try:
                        text_elements = review.find_elements(By.CSS_SELECTOR, selector)
                        if text_elements:
                            review_text = ' '.join([elem.text for elem in text_elements if elem.text])
                            if review_text:
                                print(f"Found review text with selector {selector}: {review_text[:50]}...")
                                break
                    except:
                        continue
                
                if not review_text:
                    # Last resort: get all text from the review element
                    try:
                        full_text = review.text.split('\n')
                        # Skip the first few lines which might be name and rating
                        if len(full_text) > 2:
                            review_text = ' '.join(full_text[2:])
                            print(f"Using fallback text extraction: {review_text[:50]}...")
                    except:
                        review_text = "No text found"
                
                # Extract review date
                date = "N/A"
                date_selectors = [
                    'span.rsqaWe',
                    'span.dehysf',
                    'span.xRkPPb'
                ]
                
                for selector in date_selectors:
                    try:
                        date_elements = review.find_elements(By.CSS_SELECTOR, selector)
                        if date_elements:
                            date = date_elements[0].text
                            if date:
                                print(f"Found date: {date}")
                                break
                    except:
                        continue
                
                reviews.append({
                    'Name': name,
                    'Rating': rating,
                    'Date': date,
                    'Review': review_text
                })
                
            except StaleElementReferenceException:
                print("Stale element encountered, skipping this review")
                continue
            except Exception as e:
                print(f"Error extracting a review: {e}")
                continue
        
    except Exception as e:
        print(f"Error while extracting reviews: {e}")
    
    return reviews

def scrap_page(driver, url: str):
    
    try:
        # Navigate to the URL
        driver.get(url)
        print("Loaded Google Maps page")
        time.sleep(5)
        
        # Find and click on the first business result
        if not find_first_business_and_click(driver):
            print("Could not find business listing, but continuing anyway")
        
        # Extract coordinates
        coordinates = extract_coordinates(driver)
        
        # Extract place information
        place_info = extract_place_info(driver)
        
        # Click on reviews tab
        if not click_reviews_tab(driver):
            print("Could not click reviews tab, but continuing anyway")
        
        # Scroll through reviews
        scroll_reviews(driver, scrolls=8)
        
        # Expand all reviews
        expand_all_reviews(driver)
        
        # Extract reviews
        reviews = extract_reviews(driver)
        
        # Save to CSV
        if reviews:
            review_df = pd.DataFrame(reviews)
            
            # Add place information to each review
            review_df['Place_Name'] = place_info["name"]
            review_df['Address'] = place_info["address"]
            review_df['Phone'] = place_info["phone"]
            review_df['Website'] = place_info["website"]
            review_df['Place_Rating'] = place_info["rating"]
            review_df['Total_Reviews'] = place_info["total_reviews"]
            review_df['Categories'] = place_info["categories"]
            review_df['Latitude'] = coordinates["latitude"]
            review_df['Longitude'] = coordinates["longitude"]
            
            # Save to CSV
            review_df.to_csv(f'outputs/{place_info["name"]}_info.csv', index=False, encoding='utf-8-sig')
            print(f"Successfully scraped {len(reviews)} reviews and saved to comrez_akabane_reviews.csv")
            
            # Also save place info separately
            place_data = {
                "Name": place_info["name"],
                "Address": place_info["address"],
                "Phone": place_info["phone"],
                "Website": place_info["website"],
                "Rating": place_info["rating"],
                "Total_Reviews": place_info["total_reviews"],
                "Categories": place_info["categories"],
                "Latitude": coordinates["latitude"],
                "Longitude": coordinates["longitude"]
            }
            
            place_df = pd.DataFrame([place_data])
            place_df.to_csv(f'outputs/{place_info["name"]}_reviews.csv', index=False, encoding='utf-8-sig')
            print("Place information saved to comrez_akabane_place_info.csv")
            
        else:
            print("No reviews found.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the browser
        if review_df:
            return (review_df, place_df)
        else: 
            return (None, None)
        # Uncomment the line below when ready to close the browser automatically
        # driver.quit()

def get_urls_from_file(folder_path: str) -> list:
    """Read URLs from a file and return them as a list."""
    urls = []
    url_template = "https://www.google.com/maps/search/{query}"
    file_paths = [os.path.join(folder_path, x) for x in os.listdir(folder_path)]
    
    if os.path.exists(f"{folder_path}_urls.txt"):
        with open(f"{folder_path}_urls.txt", 'r') as file:
            urls = [line.strip() for line in file.readlines()]
    else:
        for file_path in file_paths:
            with open(file_path, 'r') as file:
                data = file.readlines()[1:]
            for line in data:
                place = line.split(",")[2].strip()
                place = place.replace(" ", "+")
                url = url_template.format(query=place)
                if "line" not in url.lower():
                    urls.append(url)
        
        with open(f'{folder_path}_urls.txt', 'w') as file:
            for url in urls:
                file.write(url + "\n")
    return urls

def main():

    driver = setup_driver()

    # URL of the Google Maps page    

    urls = get_urls_from_file("scraped_locations")

    try:
        for url in urls:
            print("-----------------------------------------------------------------------------------")
            print(f"Scraping URL: {url}")
            try:
                _, _ = scrap_page(driver, url)
            except Exception as e:
                print(f"scrape_page function errored {url}: {e}")
                continue
    except Exception as e:
        print(f"An error occurred while scraping: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()