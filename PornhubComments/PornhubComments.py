import discord
from discord.ext import commands
import re
import aiohttp
import html5lib
from bs4 import BeautifulSoup
import datetime
import time

class PornhubComments:
    """Pulls comments from pornhub based on a like threshold"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="phcomments", aliases=["phc"])
    async def pornhubcomments(self, max_comments: int, max_pages: int, vote_threshold: int, entry_url="https://www.pornhub.com/"):
        """ Takes max comments,pages and like threshold e.g. !phc 50 10 100 """
        async def crawl(max_comments=max_comments, max_pages=max_pages, votes_threshold=vote_threshold):
            explored_pages = []
            page_links = []
            good_comments = {}
            
            page_links, good_comments, comments = await get_good_comments(entry_url, max_comments, good_comments, votes_threshold)
            
            await self.bot.say("Sniffing around Pornhub for the best comments...")
            
            while comments < max_comments and len(explored_pages) < max_pages:
                url =  page_links.pop()
                
                while url in explored_pages:
                    url =  page_links.pop()
                
                explored_pages.append(url)
                
                new_page_links, new_good_comments, new_comments = await get_good_comments(url, max_comments, good_comments, votes_threshold)

                comments += new_comments
             
                for link in new_page_links:
                    if link not in page_links:
                        page_links.append(link)
                
                good_comments = {**good_comments, **new_good_comments}

            async def create_embed(good_comments):
                embed = discord.Embed(colour=discord.Colour(0xc27c0e), url="https://pornhub.com")

                embed.set_image(url="https://ci.phncdn.com/www-static/images/pornhub_logo_straight.png?cache=2017092101")
                embed.set_thumbnail(url="https://ci.phncdn.com/www-static/images/pornhub_logo_straight.png?cache=2017092101")
                embed.set_footer(text="Pornhub Comments by STIGYFishh")
                
                fields = 0
                char_count = 0

                for url in good_comments.keys():
                    embed_text = ""
                    for votes, comment in good_comments[url].items():
                        if (char_count + (len(votes) + len(comment))) < 2000 and fields < 25:
                            embed_text += "{}: {}\n".format(votes, comment)
                        else:
                            embed.add_field(name=url, value=embed_text)
                            await self.bot.say(embed=embed)
                            return
                    
                    embed.add_field(name=url, value=embed_text)
                    fields += 1

                await self.bot.say(embed=embed)
                
            await create_embed(good_comments)

        async def get_good_comments(url, max_comments, good_comments, votes_threshold):
            async with aiohttp.get(url) as page:
                soup = BeautifulSoup(await page.text(), "html5lib")
                page.close()

            good_comments[url] = {}
            comments = 0
            
            for comment_block in soup.findAll("div", {"class" : "commentMessage"}):
                comment = comment_block.findAll("span")[0]
                vote_count = comment_block.find("span", {"class": "voteTotal"})
                

                if int(vote_count.text) > votes_threshold and comments < max_comments:
                    good_comments[url].update({vote_count.text: comment.text})
                    comments += 1
            
            if not good_comments[url]:
                del good_comments[url]
            
            page_links = await get_links(await page.text())
                
            return page_links, good_comments, comments

         
        async def get_links(page_content):
            page_links = []
            for link in BeautifulSoup(page_content, "html5lib").findAll("a", href=True):
                video_link = re.search("^\/view_video.php\?viewkey=[a-zA-Z0-9]{5,15}", link['href'])
                if video_link:
                    full_link = "https://www.pornhub.com" + video_link.group(0)
                    if full_link not in page_links:
                        page_links.append(full_link)
            return page_links
            
        await crawl()

def setup(bot):
    bot.add_cog(PornhubComments(bot))
