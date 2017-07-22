
import requests, re, json, time, random
requests.packages.urllib3.disable_warnings()
from http.cookies import SimpleCookie
import logging

# Created by Alex Beals
# Last updated: February 20, 2016


# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
# try:
    # import http.client as http_client
# except ImportError:
    # # Python 2
    # import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1


# You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


base_url = "https://polldaddy.com/poll/"
redirect = ""

useragents = []
current_useragent = ""

proxies = []
current_proxy = "127.0.0.1"
current_proxy_num = -1


def get_all_useragents():
    f = open("useragent.txt", "r")
    for line in f:
        useragents.append(line.rstrip('\n').rstrip('\r'))
    f.close()

def choose_useragent():
    k = random.randint(0, len(useragents)-1)
    current_useragent = useragents[k]
    #print current_useragent

def get_all_proxies():
    f = open("c.txt", "r")
    for line in f:
        proxies.append(line.rstrip('\n').rstrip('\r'))
    f.close()

def choose_proxy():
    k = random.randint(0, len(proxies)-1)
    current_num = k
    current_proxy = proxies[k]
    return current_proxy


def vote_once(form, value):
    global timeout
    c = requests.Session()
    #Chooses useragent randomly
    choose_useragent()
    redirect = {"Referer": base_url + str(form) + "/", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "User-Agent": current_useragent, "Upgrade-Insecure-Requests":"1", "Accept-Encoding": "gzip, deflate, sdch", "Accept-Language": "en-US,en;q=0.8", "Host": Host}

    # Chooses proxy randomly
    c_ip = choose_proxy()
    try:
        url = "https://" + c_ip + '/poll/' + str(form) + "/";
        print(">>>>> " + url)
        init = c.get(url, headers=redirect, verify=False, timeout=timeout)
        cookie_str = init.headers['Set-Cookie']
        # print("Cookie: " + cookie_str)
    except requests.ConnectionError, e:
        print(e)
        #proxies.remove(current_proxy_num)
        return None
    except Exception as err:
        print(err)
        return None




    # Search for the data-vote JSON object
    data = re.search("data-vote=\"(.*?)\"",init.text).group(1).replace('&quot;','"')
    # print("Data: " + data)
    data = json.loads(data)
    # Search for the hidden form value
    pz = re.search("type='hidden' name='pz' value='(.*?)'",init.text).group(1)
    # print("pz: " + pz)
    # Build the GET url to vote
    vote_url = "https://" + c_ip + "/vote.php?va=" + str(data['at']) + "&pt=0&r=2&p=" + str(form) + "&a=" + str(value) + "%2C&o=&t=" + str(data['t']) + "&token=" + str(data['n']) + "&pz=" + str(pz)
    print("Voting... " + vote_url)
    try:
        cookie = SimpleCookie()
        cookie_str += '; ' + 'PDjs_poll_9777773=' + str(int(time.time()*1000-40000))
        cookie.load(cookie_str)
        cookie = {key: value.value for key, value in cookie.items()}
        # print(">"*10 + "Cookie" + ">"*10)
        # print(cookie)
        # print("<"*10 + "Cookie" + "<"*10)
        send = c.get(vote_url, headers=redirect, verify=False, cookies=cookie, timeout=timeout)
    except requests.ConnectionError, e:
        print(e)
        #proxies.remove(current_proxy_num)
        return None
    # print(send.headers)
    print(">"*10 + "Redirected URL: " + send.url)
    return("msg=voted" in send.url)
    # return ("revoted" in send.url)

def vote(form, value, times, wait_min = None, wait_max = None):
    global redirect
    # For each voting attempt
    for i in xrange(1, times+1):
        print "\n"*2
        b = vote_once(form, value)
        # If successful, print that out, else try waiting for 60 seconds (rate limiting)
        if b:
            # Randomize timing if set
            if wait_min and wait_max:
                seconds = random.randint(wait_min, wait_max)
            else:
                seconds = 3

            print "Voted (time number " + str(i) + ")!"
            time.sleep(seconds)
        else:
            print "Locked(Connection timeout/Revoted).  Sleeping for 10 seconds."
            i-=1
            time.sleep(10)

# Initialize these to the specific form and how often you want to vote
poll_id = 0
answer_id = 0
number_of_votes = 1000
Host = "www.abc.com"
wait_min = 1
wait_max = 5
timeout=5

get_all_proxies()
get_all_useragents()
vote(poll_id, answer_id, number_of_votes, wait_min, wait_max)
