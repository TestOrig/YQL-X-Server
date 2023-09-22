import feedparser, datetime

def GetBlogPosts():
    feed = feedparser.parse("https://1pwn.ixmoe.com/feed/")
    posts = []
    for post in feed.entries:
        date_str = post.published
        date_obj = datetime.datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
        epoch_time = int(date_obj.timestamp())
        posts.append({"title": post.title, "link": post.link, "published": epoch_time})
    return posts