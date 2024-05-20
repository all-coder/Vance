import asyncpraw
import random
import tokens
from asyncprawcore.exceptions import RequestException

class Vance_Reddit:
    def __init__(self):
        self.token = tokens.reddit_token
        self.categories = {
            "Memes": ["memes", "HistoryMemes", "meme", "shitposting", "Jokes", "dadjokes", "RelationshipMemes", "dankmemes", "Animemes", "GymMemes", "terriblefacebookmemes", "ComedyCemetery", "okbuddyretard"],
            "Cricket": ["Cricket", "IndiaCricket", "CricketShitPost", "EnglandCricket"],
            "Gaming/PC": ["pcmasterrace", "buildapc", "GamingDetails", "IndieGaming", "IndianGaming", "linux_gaming", "GirlGamers", "Games"],
            "News": ["news", "UpliftingNews", "InternationalNews", "politics", "worldnews", "NewsOfTheWeird", "PupliftingNews"],
            "Wholesome": ["wholesome", "wholesomememes", "MadeMeSmile", "wholesomegifs"],
            "cringe": ["cringe", "CringePurgatory", "cringepics", "CringeTikToks", "teenagers", "FirstResponderCringe"],
            "Dark Humor": ["DarkMemesPh", 'DarkMemes', "darksoulsmemes", "Animemes", "DarkJokesWithoutHate", "ReallyDarkDadJokes", "darkjokes2"],
            "Life/Advice/Experiences": ["AskReddit", "getdisciplined", "AskMen", "DepressionBuddies", "Showerthoughts", "UncensoredAdvice", "LifeProTips"],
            "Programming": ["programming", "AskProgramming", "C_Programming", "learnprogramming", "ProgrammerHumor", "cscareerquestions", "GraphicsProgramming"],
            "Android": ["Android", "AndroidGaming", "androiddev", "AndroidAuto", "EmulationOnAndroid", "GooglePixel", "oneplus"],
            "IOS": ['ios', 'slide_ios', 'IOSsetups', 'jailbreak', 'apple', 'iphone', 'iosgaming', 'LegacyJailbreak', 'iOSProgramming']
        }
        self.reddit = None
    
    async def reddit_initialization(self):
        self.reddit = asyncpraw.Reddit(
            client_id=self.token[0],
            client_secret=self.token[1],
            user_agent=self.token[2]
        )

    def get_random_recommendations(self):
        interest_choices = random.sample(list(self.categories.keys()), 7)
        recommend_choices = [random.choice(self.categories[i]) for i in interest_choices]
        final_choices = random.sample(recommend_choices, 5)
        return final_choices
    
    async def get_posts(self, subreddits,option="hot",post_limit=2):
        all_posts = []
        for i in subreddits:
            try:
                r = await self.reddit.subreddit(i)
                if(option.lower()=="hot"):
                    posts = r.hot(limit=post_limit)
                elif(option.lower() =="top"):
                    posts = r.top(limit=post_limit)
                async for post in posts:
                    structure = {
                        'Title': post.title,
                        'Author': "Redditor: "+str(post.author),
                        'Score': post.score,
                        'URL': post.url,
                        'Content': post.selftext if post.selftext else "No content",
                        'Media': "No media attached"
                    }
                    if post.media and 'reddit_video' not in post.media:
                        if 'reddit_image_preview' in post.media:
                            structure['Media'] = post.media['reddit_image_preview']['source']['url']
                        elif 'oembed' in post.media and 'url' in post.media['oembed']:
                            structure['Media'] = post.media['oembed']['url']
                            
                    all_posts.append(structure)
            except RequestException as e:
                print(f"RequestException: {e}")
            except Exception as e:
                print(f"An error occurred: {e}")
        return all_posts
    
    async def recommend(self):
        await self.reddit_initialization()
        choices = self.get_random_recommendations()
        posts = await self.get_posts(choices)
        print(posts)
        return posts
    
    async def top_post_subreddit(self,subreddit,limit=5):
        await self.reddit_initialization()
        posts = await self.get_posts([subreddit],option="top",post_limit=limit)
        print(posts)
        return posts
        


