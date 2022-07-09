import bs4

def getcookies(session):
    return session.get("https://sims.sit.ac.in/parents/index.php").cookies

def scrape(text):
    soup = bs4.BeautifulSoup(text, "lxml")
    main_data = soup.div( attrs={"class": "uk-card uk-card-body cn-stu-data cn-stu-data1"})[0]
    return "https://sims.sit.ac.in/parents/" + main_data.img.get("src"), main_data.h3.text

def addzero(number, digit=2):
    number = str(number)
    while len(number) != digit:
        number = "0" + number
    return number


def check_is_the_page(html_str):
    return html_str.find("<option") == -1

def addtohtml(html_data):
        return f"""\n<div style="border: 8px solid;padding-left: 25px;padding-top: 25px;">   <img src="{html_data[2]}">   <h1>{html_data[0]}</h1>  <h2>{html_data[1]}</h2>  <h2>{html_data[3]}</h2>  </div>   \n"""
    
