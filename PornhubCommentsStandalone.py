import re
import requests
import html5lib
from bs4 import BeautifulSoup
import argparse

def crawl(max_comments=10, max_pages=10, votes_threshold=50, entry_url="https://www.pornhub.com/"):
    explored_pages = []
    page_links = []
    good_comments = {}
    
    page_links, good_comments, comments = get_good_comments(entry_url, max_comments, good_comments, votes_threshold) 
    
    while comments < max_comments or len(explored_pages) < max_pages:
        url =  page_links.pop()
        
        while url in explored_pages:
            url =  page_links.pop()
        
        explored_pages.append(url)
        
        new_page_links, new_good_comments, new_comments = get_good_comments(url, max_comments, good_comments, votes_threshold)
        
        comments += new_comments
        
        for link in new_page_links:
            if link not in page_links:
                page_links.append(link)
        
        good_comments = {**good_comments, **new_good_comments}
    
    for url in good_comments.keys():
       print("Video URL:", url)
       for votes, comment in good_comments[url].items():
            print(votes + ":", comment)
       print("\n")
        
        
def get_good_comments(url, max_comments, good_comments, votes_threshold):
    page = requests.get(url)   
    soup = BeautifulSoup(page.text, "html5lib")
    
    good_comments[url] = {}
    comments = 0
    
    for comment_block in soup.findAll("div", {"class" : "commentMessage"}):
        comment = comment_block.findAll("span")[0]
        vote_count = comment_block.find("span", {"class": "voteTotal"})
        
        if int(vote_count.text) > votes_threshold and comments > max_comments:
            good_comments[url].update({vote_count.text: comment.text})
            comments += 1
    
    if not good_comments[url]:
        del good_comments[url]
    
    page_links = get_links(page.text)
    
    return page_links, good_comments, comments

 
def get_links(page_content):
    page_links = []
    for link in BeautifulSoup(page_content, "html5lib").findAll("a", href=True):
        video_link = re.search("^\/view_video.php\?viewkey=[a-zA-Z0-9]{5,15}", link["href"])
        if video_link:
            full_link = "https://www.pornhub.com" + video_link.group(0)
            if full_link not in page_links:
                page_links.append(full_link)
    return page_links
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--comment-count", nargs="?", default=10, type=int)
    parser.add_argument("-p", "--page-count", nargs="?", default=10, type=int)
    parser.add_argument("-v", "--vote-count", nargs="?", default=50, type=int)
    parser.add_argument("-e", "--entry-url", nargs="?", default="https://www.pornhub.com", type=str)

    args = parser.parse_args()
    crawl(args.comment_count, args.page_count, args.vote_count, args.entry_url)


    