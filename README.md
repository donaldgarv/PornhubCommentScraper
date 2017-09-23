# PornhubCommentScraper
Pornhub Comment scraper for discord.py

takes the optional arguments:

comment count
minimum votes
max number of pages to crawl
entry url

Usage: ./PornhubComments.py -c 10 -v 50 -p 5 -e https://www.pornhub.com/view_video.php?viewkey=ph59aa47fc1d728

Theres also a discord cog, this is tested working with Red and NotSoBot. 
You can use the !cog repo command to pull it into Red.

### Discord Cog Issues with Python3.6 ###
As of Python 3.6 aiohttp errors out when multiple requests are made concurrently, so don't spam it.
Seems to be stable in Python 3.5.3, occassioanly spits a pause_rerading() error, but does not affect output.



