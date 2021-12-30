import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from decouple import config

from CSV import CSV
from JSON import JSON
from NFT import NFT

EXTENSION_PATH = config("EXTENSION_PATH")
RECOVERY_CODE = config("RECOVERY_CODE")
PASSWORD = config("PASSWORD")
CHROME_DRIVER_PATH = config("CHROME_DRIVER_PATH")

COLLECTION_NAME = config("COLLECTION_NAME")
CREATE_URL = "https://opensea.io/collection/" + COLLECTION_NAME + "/assets/create"

def checkInt(str):
    try:
        int(str)
        return True
    except ValueError:
        return False

def setup_metamask_wallet(d):
    d.switch_to.window(d.window_handles[0])  # focus on metamask tab
    time.sleep(5)
    d.find_element(By.XPATH, '//button[text()="Get Started"]').click()

    time.sleep(1)
    d.find_element_by_xpath('//button[text()="Import wallet"]').click()
    time.sleep(1)

    d.find_element_by_xpath('//button[text()="No Thanks"]').click()
    time.sleep(1)

    inputs = d.find_elements_by_xpath("//input")
    inputs[0].send_keys(RECOVERY_CODE)
    inputs[1].send_keys(PASSWORD)
    inputs[2].send_keys(PASSWORD)
    time.sleep(1)

    d.find_element_by_css_selector(".first-time-flow__terms").click()
    d.find_element_by_xpath('//button[text()="Import"]').click()


def move_to_opensea(d):
    d.execute_script("window.open(\"" + CREATE_URL + "\",\"_blank\")")
    d.switch_to.window(d.window_handles[2])
    time.sleep(3)


def signin_to_opensea(d):
    time.sleep(4)
    d.find_element_by_xpath('//span[text()="MetaMask"]').click()
    time.sleep(4)
    d.switch_to.window(d.window_handles[2])
    time.sleep(2)
    d.find_element_by_xpath('//span[text()="MetaMask"]').click()
    time.sleep(4)
    d.switch_to.window(d.window_handles[4])
    time.sleep(2)
    d.find_element_by_xpath('//button[text()="Next"]').click()
    time.sleep(1)
    d.find_element_by_xpath('//button[text()="Connect"]').click()
    time.sleep(3)
    d.find_element_by_xpath('//button[text()="Sign"]').click()


def fillMetadata(d: webdriver.Chrome, metadataMap: dict):

    # PROPERTIES
    trait_classes = [
        d.find_element_by_xpath('//div[@class="AssetFormTraitSection--side"]/button'),
        d.find_element_by_xpath('(//div[@class="AssetFormTraitSection--side"])[2]/button'),
        d.find_element_by_xpath('(//div[@class="AssetFormTraitSection--side"])[3]/button')    
    ]
    trait_class_index = 1

    for trait_class in trait_classes:
        trait_class.send_keys(Keys.ENTER)

        for key in metadataMap:
            display_type = None
            trait_type = "Property"
            value = None
            max = None
            is_number = False
            entries = len(key)

            if "display_type" in key:
                display_type = str(key["display_type"])
            # LEVEL traits shouldn't have display types
            if trait_class_index == 2 and (display_type != None):
                continue
            # NUMERICAL traits should have display types
            if trait_class_index == 3 and (display_type == None):
                continue

            if "trait_type" in key:
                trait_type = str(key["trait_type"])

            if "value" in key:
                value = str(key["value"])
                is_number = checkInt(value)
            else:
                print("<!> Trait without value:", trait_type)
                continue
            if is_number:
                # skip if it's a number, trait properties don't deal with numbers
                if trait_class_index == 1:
                    continue
            else:
                # levels or numericals NEED a number to continue
                if trait_class_index > 1:
                    continue

            if "max" in key:
                if checkInt(key["max"]):
                    max = int( key["max"] )
                else:
                    continue # skip if there is a max, but it's not a number

            # custom max values
            if max == None:
                max = str( value )

            # get & set the input fields
            input3 = None
            if is_number:
                input3 = d.find_element_by_xpath('//tbody[@class="AssetTraitsForm--body"]/tr[last()]/td[3]/div/div/input')
                input3.send_keys(Keys.CONTROL,"a")
                input3.send_keys(max)

            input2 = d.find_element_by_xpath('//tbody[@class="AssetTraitsForm--body"]/tr[last()]/td[2]/div/div/input')
            input2.send_keys(Keys.CONTROL,"a")
            input2.send_keys(value)

            input1 = d.find_element_by_xpath('//tbody[@class="AssetTraitsForm--body"]/tr[last()]/td[1]/div/div/input')
            input1.send_keys(Keys.CONTROL,"a")
            input1.send_keys(trait_type)

            d.find_element_by_xpath('//button[text()="Add more"]').send_keys(Keys.ENTER)

        time.sleep(1)
        d.find_element_by_xpath('//button[text()="Save"]').send_keys(Keys.ENTER)
        time.sleep(1)
        trait_class_index += 1


def upload(d, nft: NFT):
    d.switch_to.window(driver.window_handles[-1])
    time.sleep(1)
    d.find_element_by_id("media").send_keys(nft.file)
    time.sleep(1)
    d.find_element_by_id("name").send_keys(nft.name)
    d.find_element_by_id("description").send_keys(nft.description)

    d.find_element_by_id("external_link").send_keys(nft.external_url)
    d.find_element_by_id("unlockable-content-toggle").send_keys(Keys.ENTER)
    d.find_element_by_xpath('//div[@class="AssetForm--unlockable-content"]/textarea').send_keys(nft.unlockable_content)

    time.sleep(1)

    fillMetadata(d, nft.metadata)

    time.sleep(1)
    d.find_element_by_xpath('//button[text()="Create"]').send_keys(Keys.ENTER)
    time.sleep(4)
    d.execute_script("location.href=\"" + CREATE_URL + "\"")


if __name__ == '__main__':
    # setup metamask
    opt = webdriver.ChromeOptions()
    exists = os.path.isfile(EXTENSION_PATH)
    if exists:
        print(">> exists")
    else:
        print(">>> NOT EXIST!!")
    opt.add_extension(EXTENSION_PATH)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, chrome_options=opt)
    setup_metamask_wallet(driver)
    time.sleep(2)
    move_to_opensea(driver)
    signin_to_opensea(driver)
    driver.execute_script("window.open(\"" + CREATE_URL + "\",\"_blank\")")
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(3)  # todo- need to manually click on sign button for now

#1--299
#1405-1437
    first_id = 300
    last_id = 500-1

    for i in range(first_id, (last_id+1)):
        path = os.getcwd() + "/data/metadata/" + str(i) + ".json"
        data = JSON(path).readFromFile()
        name = data["name"]
        description = data["description"]
        file = os.getcwd() + "/data/images/" + str(i) + ".png"
        metadata = data["attributes"]
        unlockable_content = data["unlockable_content"]
        ext_url = data["external_url"]
        upload(driver, NFT(name, description, unlockable_content, ext_url, metadata, file))
        print("> Successfully uploaded", name)
        time.sleep(1)

    print("DONE!!")

