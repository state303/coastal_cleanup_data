import time

import env
from browser import ChromeBrowser as Browser
from parser import parse
from update import run
from utils import *

ENDPOINT_BASE = "https://www.coastalcleanupdata.org"
ENDPOINT_LOGIN = ENDPOINT_BASE + "/login"
ENDPOINT_REST = ENDPOINT_BASE + "/rest/report"
DEFAULT_ZONE = "poly-5&poly%5B0%5D%5Blat%5D=84.46384633002378&poly%5B0%5D%5Blng%5D=-173.80720065504943&poly%5B1%5D%5Blat%5D=66.61092806952752&poly%5B1%5D%5Blng%5D=-158.69001315504943&poly%5B2%5D%5Blat%5D=62.99489705778867&poly%5B2%5D%5Blng%5D=-167.9765010230767&poly%5B3%5D%5Blat%5D=7.187529722754638&poly%5B3%5D%5Blng%5D=-172.1952510230767&poly%5B4%5D%5Blat%5D=7.187529722754638&poly%5B4%5D%5Blng%5D=-149.6952510230767&poly%5B5%5D%5Blat%5D=-13.753283832083639&poly%5B5%5D%5Blng%5D=-143.3671260230767&poly%5B6%5D%5Blat%5D=-16.468246805700407&poly%5B6%5D%5Blng%5D=-168.6796260230767&poly%5B7%5D%5Blat%5D=-39.50448488134843&poly%5B7%5D%5Blng%5D=-167.2733760230767&poly%5B8%5D%5Blat%5D=-43.961605012349885&poly%5B8%5D%5Blng%5D=-33.679626023076764&poly%5B9%5D%5Blat%5D=-41.64050860253925&poly%5B9%5D%5Blng%5D=94.99224897692324&poly%5B10%5D%5Blat%5D=-46.1954405909191&poly%5B10%5D%5Blng%5D=124.69928022692329&poly%5B11%5D%5Blat%5D=-46.43825361301273&poly%5B11%5D%5Blng%5D=133.4883427269233&poly%5B12%5D%5Blat%5D=-61.407555298594225&poly%5B12%5D%5Blng%5D=160.45694136260363&poly%5B13%5D%5Blat%5D=-39.04530366566861&poly%5B13%5D%5Blng%5D=-174.93368363739637&poly%5B14%5D%5Blat%5D=-6.948900216316141&poly%5B14%5D%5Blng%5D=-173.17587113739637&poly%5B15%5D%5Blat%5D=-3.097301371826066&poly%5B15%5D%5Blng%5D=178.73819136260363&poly%5B16%5D%5Blat%5D=43.62764099460053&poly%5B16%5D%5Blng%5D=178.03506636260363&poly%5B17%5D%5Blat%5D=54.20062038873039&poly%5B17%5D%5Blng%5D=165.02725386260363&poly%5B18%5D%5Blat%5D=66.39889316615911&poly%5B18%5D%5Blng%5D=-170.71493363739637&poly%5B19%5D%5Blat%5D=72.52133133225857&poly%5B19%5D%5Blng%5D=178.73819136260363&poly%5B20%5D%5Blat%5D=84.64686783016302&poly%5B20%5D%5Blng%5D=176.98037886260363&poly%5B21%5D%5Blat%5D=84.41229813433394&poly%5B21%5D%5Blng%5D=34.24600386260363&poly%5B22%5D%5Blat%5D=84.27368667485489&poly%5B22%5D%5Blng%5D=-93.42977381111763"
BASE_FILE_NAME = "coastalcleanupdata_{}.csv"


def get_download_url(year: int) -> str:
    endpoint = ENDPOINT_REST + "?zone={}&filter%5BfromDate%5D={}&filter%5BtoDate%5D={}&download=true"
    return endpoint.format(DEFAULT_ZONE, "{}-01-01".format(year), "{}-12-31".format(year))


def fetch_inventories(b: Browser):
    current_year = get_current_year()
    success = True
    begin, end = get_year_range()
    for year in range(begin, end + 1):
        print("fetching target from year {} - {}".format(2016, current_year + 1))
        filepath = BASE_FILE_NAME.format(year)
        if os.path.isfile(filepath) and os.path.getsize(filepath) > 0:
            print("already exists: {}. skipping..".format(filepath))
            continue
        try:
            b.navigate(get_download_url(year), timeout=30, validate=False)
            time.sleep(20)
            src_path = find("detailed-summary-custom-polygon.csv", os.getcwd())
            if src_path is None:
                print("failed to fetch item for year: {}".format(year))
            else:
                with open(filepath, "w") as dst, open(src_path, "r") as src:
                    print("written to {}: {} bytes".format(filepath, dst.write(src.read())))
                os.remove(src_path)
        except Exception as e:
            print("failed to request CSV for year {}.\nerror: {}".format(year, e))
            success = False
            break
    if not success:
        raise (Exception("failed to acquire inventories. exiting..."))
    print("successfully acquired inventories")


def login(driver: Browser):
    username, password = read_credentials()
    driver.navigate(ENDPOINT_LOGIN)
    try:
        driver.find_elements_by_id("username")[0].send_keys(username)
        print("username inserted")
        time.sleep(0.5)

        driver.find_elements_by_id("password")[0].send_keys(password)
        print("password inserted")

        driver.find_elements_by_id("remember_me")[0].click()
        print("clicked remember_me")

        driver.find_elements_by_id("_submit")[0].click()
        print("submitted login")
    except Exception as e:
        print(e)
        exit(1)

    # verify redirection
    for i in range(10):
        time.sleep(1)
        if driver.get_url() != "https://www.coastalcleanupdata.org/":
            continue
        else:
            break
    print("login verified")

    time.sleep(10)
    # check login
    el = driver.find_elements_by_css_selector("ul.nav:nth-child(1) > li:nth-child(1) > strong:nth-child(1)")[0]
    if el.text.find("Welcome") < 0:
        exit(1)
    else:
        print("login successful")


def main():
    b = Browser()
    try:
        login(b)
        print("login successful")
        fetch_inventories(b)
        print("fetched inventories")
    except Exception as e:
        print(e)
    finally:
        if b:
            b.close()
    print("beginning yearly batch processing..")
    for year in range(env.min_year, env.max_year + 1):
        print(f"processing year {year}")
        items = parse(year)
        run(items)
        print(f"data processed for year {year}")


if __name__ == '__main__':
    main()
