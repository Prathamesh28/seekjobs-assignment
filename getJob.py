import json
from urllib import parse
import requests
from bs4 import BeautifulSoup


def elemToObject(title,elem,start):

    # Get all childrens of the element
    children = list(elem.descendants)

    # Filter the newline tags
    children = list(filter(lambda t : t != "\n",children))
    text_list = []

    # Extracting the text from the children elements
    for i in range(start, len(children), 2):
        text_list.append(children[i].text)
    #Creating an object with title and list of points
    obj = {}
    obj["title"] = title
    obj["list"] = text_list
    return obj

def getUrls(URL):
    # Requests the page
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")

    # Get all openings
    job_elements = soup.find_all("div", class_="opening")
    job_ids = []
    for job_element in job_elements:
        # Fetch href of all openings
        for i in job_element.find_all("a"):
            url = i["href"]
            job_id = parse.parse_qs(parse.urlparse(url).query)['gh_jid'][0]
            job_ids.append(job_id)
    return job_ids

def getObj(soup,headings,start = 2):
    # Get element containing the required heading in <strong> tag
    title = soup.find("strong",string=lambda text: text != None and headings[0] in text.lower())
    # If not found previously then search in <span> tags
    if not title :
        title = soup.find("span",string=lambda text: text != None and headings[1] in text.lower())
    elem = []
    # If the heading exist the go to next element to fetch info for that title
    if title :
        elem = title.parent.find_next_sibling()
    else:
        return None
    
    return elemToObject(title.text,elem,start)


def getJobs(URL):
    job_ids = getUrls(URL)
    data = []
    for job_id in job_ids:
        base_url = 'https://boards.greenhouse.io/embed/job_app?for=coursera&token='
        page = requests.get(base_url + job_id)
        job = {}
        job["details"] = []
        soup = BeautifulSoup(page.content,"html.parser")
        job_title = soup.find("h1", class_="app-title").text.strip()
        job_location = soup.find("div", class_="location").text.strip()

        apply_link = "https://about.coursera.org/careers/jobs/?gh_jid=" + job_id


        job["job_title"] = job_title
        job["job_location"] = job_location
        job["apply_link"] = apply_link
        job["job_id"] = job_id

        overview = getObj(soup,["job overview","job overview"],1)
        if overview:
            job["details"].append(overview)
        responsibilities = getObj(soup,["responsibilities","responsibilities"])
        if responsibilities:
            job["details"].append(responsibilities)
        basicQualification = getObj(soup,["basic qualifications","your skill"])
        if basicQualification:
            job["details"].append(basicQualification)
        preferredQualification = getObj(soup,["preferred qualification","preferred qualification"])
        if preferredQualification:
            job["details"].append(preferredQualification)
        
        

        data.append(job)
    return data

if __name__ == "__main__":

    URL = 'https://boards.greenhouse.io/embed/job_board?for=coursera'
    data = getJobs(URL)

    # Write data to a json file
    with open("output.json","w") as file:
        json.dump(data,file,indent=4)