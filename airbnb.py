import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_data():
    read_json = json.load(open("airbnb_json.json", encoding="utf8"))

    images_url = []
    img_urls = read_json['niobeMinimalClientData'][0][1]['data']['presentation']['stayProductDetailPage']['sections']['sections']
    for i in img_urls:
        if i["__typename"]== 'SectionContainer':
            try:
                for url in i['section']['previewImages']:
                    images_url.append(url['baseUrl'])
            except:
                pass

    the_space = []
    gest_access = []
    other_things_to_note = []
    the_neighborhood = []
    summary = read_json['niobeMinimalClientData'][0][1]['data']['presentation']['stayProductDetailPage']['sections']['sections']
    for j in summary:
        if j["__typename"]== 'SectionContainer':
            try:
                summary_li = j['section']['htmlDescription']['htmlText'].replace('<br /><br />','\n').replace('</b><br />','\n').replace('<br />','\n').split('<b>')
                for i in range(len(summary_li)):
                    if i == 0:
                        summary = summary_li[0]
                    if summary_li[i].startswith('The space'):
                        the_space.append(summary_li[i].replace('\n',' '))
                    if summary_li[i].startswith('Guest access'):
                        gest_access.append(summary_li[i].replace('\n',' '))
                    if summary_li[i].startswith('Other things to note'):
                        other_things_to_note.append(summary_li[i].replace('\n',' '))
                    if summary_li[i].startswith('The neighborhood'):
                        the_neighborhood.append(summary_li[i].replace('\n',' '))
            except:
                pass


    place_offers = {}
    place_all_offers = read_json['niobeMinimalClientData'][0][1]['data']['presentation']['stayProductDetailPage']['sections']['sections']
    for i in place_all_offers:
        if i["__typename"]== 'SectionContainer':
            try:
                for title in i['section']['seeAllAmenitiesGroups']:
                    li = []
                    main_title = title['title']
                    for sub_title in title['amenities']:
                        li.append(sub_title['title'])
                    place_offers.update({main_title:li})
            except:
                pass
    # print(place_offers)


    sub_rating = {}
    ratings = read_json['niobeMinimalClientData'][0][1]['data']['presentation']['stayProductDetailPage']['sections']['sections']
    for i in ratings:
        if i["__typename"]== 'SectionContainer':
            try:
                for rating in i['section']['ratings']:
                    sub_rating.update({rating['label']:rating['localizedRating']})
            except:
                pass
    # print(sub_rating)

    total_rating = read_json['niobeMinimalClientData'][0][1]['data']['presentation']['stayProductDetailPage']['sections']['sections']
    for i in total_rating:
        try:
            overallrating = i['section']['overallRating']
        except:
            overallrating = ''



    total_count = read_json['niobeMinimalClientData'][0][1]['data']['presentation']['stayProductDetailPage']['sections']['sections']
    for i in total_count:
        try:
            overallcount = i['section']['overallCount']
        except:
            overallcount = ''


    house_rules = {}
    houserulesrections = read_json['niobeMinimalClientData'][0][1]['data']['presentation']['stayProductDetailPage']['sections']['sections']
    for i in houserulesrections:
        if i["__typename"]== 'SectionContainer':
            try:
                for rule_name in i['section']['houseRulesSections']:
                    li = []
                    name_rule = rule_name['title']
                    for rule in rule_name['items']:
                        li.append(rule['title'])
                    house_rules.update({name_rule:li})
            except:
                pass
    # print(house_rules)



    house_safety = {}
    safetyandpropertiessections = read_json['niobeMinimalClientData'][0][1]['data']['presentation']['stayProductDetailPage']['sections']['sections']
    for i in safetyandpropertiessections:
        if i["__typename"]== 'SectionContainer':
            try:
                for safety in i['section']['safetyAndPropertiesSections']:
                    li = []
                    title = safety['title']
                    for rule in safety['items']:
                        li.append(rule['title'])
                    house_safety.update({title:li})
            except:
                pass

    rooms_detail = {}
    rooms_detalis = read_json['niobeMinimalClientData'][0][1]['data']['presentation']['stayProductDetailPage']['sections']['sections']
    for i in rooms_detalis:
        if i["__typename"]== 'SectionContainer':
            try:
                for detail in i['section']['arrangementDetails']:
                    rooms_detail.update({detail['title']:detail['subtitle']})
            except:
                pass

    payload = {
        'image_uls':images_url,
        'summary':  ''.join(summary),
        'the_space':''.join(the_space),
        'gest_access':''.join(gest_access),
        'other_things_to_note':''.join(other_things_to_note),
        'the_neighborhood':''.join(the_neighborhood),
        'place_offers':place_offers,
        'sub_rating':sub_rating,
        'overallrating':overallrating,
        'overallcount':overallcount,
        'house_rules':house_rules,
        'safety_property':house_safety,
        'rooms_details':rooms_detail
    }
    print("yes return payload")
    return payload


def get_cats_urls():
    with sync_playwright() as p:
        url = 'https://www.airbnb.com/s/Miami--Florida--United-States/homes?flexible_trip_lengths%5B%5D=one_week&monthly_start_date=2023-12-01&monthly_length=3&query=Miami%2C%20Florida%2C%20United%20States&place_id=ChIJEcHIDqKw2YgRZU-t3XHylv8&refinement_paths%5B%5D=%2Fhomes&tab_id=home_tab&date_picker_type=calendar&source=structured_search_input_header&search_type=autocomplete_click'
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        page.goto(url)
        try:
            page.wait_for_selector('//*[@id="site-content"]/div/div[3]/div/div/div/nav/div/a[6]')
        except:
            pass
        cat_urls = []

        while True:
            response = page.content()
            soup = BeautifulSoup(response,'html.parser')
            find_div = soup.find_all('a',{'class':'l1ovpqvx bn2bl2p dir dir-ltr'})
            for url in find_div:
                cat_urls.append(url['href'])
            print(len(cat_urls))
            next_page = page.locator('//*[@aria-label="Next"]')
            try:
                if next_page:
                    next_page = page.locator('//*[@aria-label="Next"]')
                    next_page.click()
                    try:
                        page.wait_for_selector('//*[@id="site-content"]/div/div[2]/div/div/div/div/div[1]/div[18]/div/div[2]/div/div/div/div[1]/div')
                        # time.sleep()
                    except:
                        pass
            except:
                break
    return cat_urls

def get_headers(url):
    # url = 'https://www.airbnb.com/rooms/775335482037369863?adults=1&children=0&enable_m3_private_room=true&infants=0&pets=0&check_in=2023-12-30&check_out=2024-01-04&source_impression_id=p3_1698850845_5DLW4gYo%2BlMMvpoA&previous_page_section_name=1000&federated_search_id=0096f006-3aa5-4443-adc4-bb4f68d743fa'
    driver = webdriver.Firefox()
    driver.get(url)

    findelement = driver.find_element(By.XPATH, "//img[@class='itu7ddv i1mla2as i1cqnm0r dir dir-ltr']")

    head = []

    if WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//img[@class='itu7ddv i1mla2as i1cqnm0r dir dir-ltr']"))):
        count = 1
        for request in driver.requests:
            if request.url.startswith('https://www.airbnb.com/') and "cookie" in list(request.headers.keys()):
                head_dict = dict(request.headers)
                head.append(json.dumps(head_dict,indent= 4))
        print('response -->  yes get headers & headers updates')
        with open("headers.json", "w") as f:
            f.write(str(head[1]))
        driver.close() 

def get_json(url):
    while True:
        url = url
        payload = {}
        headers = json.load(open('headers.json'))

        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code  == 200:
            print(response,url)
            soup = BeautifulSoup(response.text,'html.parser')
            script_json = soup.find('script',{'id':'data-deferred-state'})
            with open('airbnb_json.json','w', encoding= 'utf-8') as f:
                f.write(script_json.text)
            print('response ---> get_json')
            break
        else:
            get_headers(url)

if __name__=='__main__':
    all_data = []
    for one_cat_url in get_cats_urls():
        print("https://www.airbnb.com"+one_cat_url)
        # get_headers("https://www.airbnb.com"+one_cat_url)
        get_json("https://www.airbnb.com"+one_cat_url)
        all_data.append(get_data())
        df = pd.DataFrame(all_data)
        df.to_json('airbnb.json',orient="records")
    # # all_data.append(dic)
    # # print(dic)
    # with open('Airbnb.json','w') as f:
    #     f.write(json.dumps(dic))