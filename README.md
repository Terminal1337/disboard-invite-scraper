# disboard-invite-scraper
Scrape Servers Off Disboard with Ease!!

![image](https://user-images.githubusercontent.com/95563109/236413451-72b03772-2aed-49b6-ac87-707e555f1a64.png)

`Pre Requirements :-`
```
pip install -r requirements.txt
```

`Setting Up config.json`
```
-> Cloudflare :-
* Challenged - true (if getting challenged by cf)
* user_agent - your browser useragent
* how to get cloudflare cookie?
- Open Disboard on browser -> go to network tab -> request headers -> cookie -> copy value

-> Settings :-
* tag - the server tag you want to scrape
* limit - number of pages you want to scrape
* discord_mode - true , if you want to scrape discord invite links directly
* debug - true, if you want to print the verification level of the server (good for raiders to find servers with 0 verification)

-> Proxy:-
* use_proxy : true, to use proxies for scraping (recommended)
* proxy_type : "http" (only supported as of now)
```
