import time
import os

username = 'torken_ci'
password = os.environ['Insta_pas']

getdriver = ("https://www.instagram.com/accounts/login/")

async def Insta_post(insta_prompt, insta_img):
  
  driver = webdriver.Firefox()
  driver.maximize_window()
  driver.get(getdriver)
  
  time.sleep(1)
  
  driver.find_element("xpath", "//input[@name='username']").send_keys(username)
  driver.find_element("xpath", "//input[@name='password']").send_keys(password)
  
  time.sleep(1)
  
  driver.find_element("xpath", "//button[contains(.,'Decline optional cookies')]").click()
  
  time.sleep(2)
  
  driver.find_element("xpath", "//button[contains(.,'Log in')]").click()
  
  time.sleep(5)
  
  
  driver.find_element("xpath", "//span[contains(., 'Create')]").click()
  
  time.sleep(0.5)
  
  driver.find_element("xpath", "//button[contains(.,'Select from computer')]").click()
  
  time.sleep(0.3)
  for index, img in enumerate(insta_img):
      pyautogui.typewrite(img)
      pyautogui.press('enter')
      time.sleep(0.1)
      print(index)
      if index+1 != len(insta_img):
          driver.find_element("xpath", "//*[@aria-label='Open media gallery']").click()
          driver.find_element("xpath", "//*[@aria-label='Plus icon']").click()
      else:
          pyautogui.press('enter, tab')
  
  
  time.sleep(0.2)
  driver.find_element("xpath", "//*[@aria-label='Select crop']").click()
  driver.find_element("xpath", "//*[@aria-label='Select crop']").click()
  
  time.sleep(0.2)
  
  driver.find_element("xpath", "//*[@aria-label='Photo outline icon']").click()
  
  time.sleep(0.2)
  
  driver.find_element("xpath", "//div[contains(., 'Crop')]").click()
  time.sleep(0.2)
  
  pyautogui.press('tab')
  pyautogui.press('tab')
  pyautogui.press('enter')
  
  pyautogui.press('tab')
  pyautogui.press('tab')
  pyautogui.press('enter')
  time.sleep(0.5)
  driver.find_element("xpath", "//*[@aria-label='Write a caption...']").click()
  pyautogui.typewrite({insta_prompt})
  
  pyautogui.press('tab')
  pyautogui.press('tab')
  pyautogui.press('tab')
  pyautogui.press('tab')
  pyautogui.press('tab')
  pyautogui.press('tab')
  pyautogui.press('enter')
  
  
  time.sleep(2)
  
  driver.quit()