import discord
from discord.ext import commands
import gitget
import asyncio
from discord import Embed
import tokens
import async_reddit


class Vance:
    def __init__(self, token):
        self.token = token
        self.intents = discord.Intents.default()
        self.intents.members = True
        self.intents.message_content = True
        self.reddit = async_reddit.Vance_Reddit()
        self.client = commands.Bot(intents=self.intents, command_prefix="v!")
        self.gg = gitget.Vance_Github()
        self.commands_list = {
            "callout": "Mentions everyone in the server (reserved only for admins)",
            "nuke": "Clears out all messages in the channel where it was invoked (admins only)",
            "create_text_channel": "Creates a text channel with the name provided (admins only), takes two arguments{category_name,[channel_names]}",
            "gh_repos": "Returns a list of github public repositories of any (actual) user provided (takes one argument{username})",
            "gh_search":"Searches through github and returns valid responses, with the query you gave",
            "reddit_today":"Returns the random reddit posts based on general preferences",
            "reddit_toppost":"Returns top posts of the subreddit that you query",
            "del_cat":"Deletes the category and channels under it"
        }
        self.vance_keys = ["hey v", "hey vance", "vance"]
        self.help_keys = ["what can you do", "show me", "help me"]

        self.initial_commands()

    def initial_commands(self):
        @self.client.event
        async def on_ready():
            print(f"Logged in as {self.client.user}")

        @self.client.event
        async def on_message(message):
            if message.author == self.client.user:
                return
            if(message.content.lower().startswith('v!') and message.content.lower()[2:] not in list(self.commands_list.keys()) and message.content.lower()!='v!'):
                await message.channel.send(f"That is not even an actual command")
            if(message.content.lower()=='v!'):
                await message.channel.send(f"Go ahead,tell me what to do, <@{message.author.id}>")
            if any(keyword in message.content.lower() for keyword in self.vance_keys):
                await message.channel.send("What can I do for you, human?")

                def check(m):
                    return m.author == message.author and m.channel == message.channel

                try:
                    reply = await self.client.wait_for('message', check=check, timeout=200)
                    if any(keyword in reply.content.lower() for keyword in self.help_keys):
                        await message.channel.send("Here is what I can do for you")
                        await message.channel.send("You need to always type the prefix : 'v!', before typing out any command")
                        for key, value in self.commands_list.items():
                            await message.channel.send(f"**{key}**: {value}")
                except Exception as e:
                    print(e)
                    await message.channel.send(f"Try again, <@{message.author.id}>")

            await self.client.process_commands(message)
        self.server_commands()

    def server_commands(self):
        @self.client.command()
        async def callout(ctx):
            if any(role.name in ["Admin", "ADMIN"] for role in ctx.author.roles):
                await ctx.send("Forgers, assemble!")
                for member in ctx.guild.members:
                    await ctx.send(f"<@{member.id}>")
            else:
                await ctx.send("You don't have permission to use this command.")

        @self.client.command()
        @commands.has_permissions(administrator=True)
        async def nuke(ctx, amount: int = 0):
            await ctx.send("Are you sure you want to nuke the messages? Type 'yes' to confirm.")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            try:
                reply = await self.client.wait_for('message', check=check, timeout=200)
                if reply.content.lower() == "yes":
                    await ctx.send("Nuking in ....")
                    for i in range(5, 0, -1):
                        await ctx.send(i)
                    if amount == 0:
                        await ctx.channel.purge(limit=None)
                        await ctx.channel.send(f"An empty channel reveals more...., isn't that right <@{ctx.author.id}>?")
                    else:
                        await ctx.channel.purge(limit=amount+8)
                elif reply.content.lower() == 'no':
                    await ctx.send(f"Try gaining courage next time,<@{ctx.author.id}>")

            except Exception as e:
                print(e)
                await ctx.send(f"Failed to nuke messages, <@{ctx.author.id}>.")

        @self.client.command()
        @commands.has_permissions(administrator=True)
        async def create_tchannel(ctx, category_name: str, channel_name: str):
            if any(role.name in ["Admin", "ADMIN"] for role in ctx.author.roles):
                server = ctx.guild
                exist_category = discord.utils.get(server.categories, name=category_name)
                await ctx.send(f"Cooking right now..., <@{ctx.author.id}>")
                if not exist_category:
                    exist_category = await server.create_category(category_name)
                    await ctx.send(f"{category_name} category, initially not present, now created")
                channels_list = channel_name.split(',')
                for i in channels_list:
                    name = i.strip()
                    exist_channel = discord.utils.get(server.channels, name=name)
                    if not exist_channel:
                        await server.create_text_channel(name, category=exist_category)
                        await ctx.send(f"{i} channel created,<@{ctx.author.id}>")
                    else:
                        await ctx.send(f"{i} channel already present, try a new one")
            else:
                await ctx.send(f"Who are you, kid?, <@{ctx.author.id}>")

        @self.client.command()
        @commands.has_permissions(administrator=True)
        async def del_cat(ctx, category_name: str):
            if any(role.name in ["Admin", "ADMIN"] for role in ctx.author.roles):
                pass
            else:
                ctx.reply(f"You lack the power to enforce the following command,<@{ctx.author.id}>")
            if len(category_name) == 0:
                await ctx.reply(f"Enter a category name to delete it, <@{ctx.author.id}>")
            else:
                server = ctx.guild
                exist_category = discord.utils.get(server.categories, name=category_name)
                if exist_category:
                    channels_list = [i for i in server.channels if i.category == exist_category]
                    if len(channels_list) == 0:
                        await exist_category.delete()
                        await ctx.reply(f"Category successfully deleted,<@{ctx.author.id}>")
                    else:
                        for i in channels_list:
                            await i.delete()
                        await exist_category.delete()
                        await ctx.reply(f"Category successfully deleted,<@{ctx.author.id}>")
                else:
                    await ctx.reply("Category not found.")

        @self.client.command()
        async def gh_repo(ctx, username: str = ""):
            if len(username) == 0:
                await ctx.send(f"<@{ctx.author.id}>, provide a username to list the github repos")
            else:
                repos_map = self.gg.get_github_repos(username)
                if repos_map:
                    for i in repos_map:
                        await ctx.send(f"**{i[0]}**\n{i[1]}\n{i[2]}\n\n")
                        await asyncio.sleep(1)
                else:
                    await ctx.send("Failed to get, try again,")

        @self.client.command()
        async def gh_search(ctx, query: str, query_number: int = 5, page_number: int = 1, order: str = 'desc'):
            # should add a bookmark button and maintain this in the form of a sql table.
            query_result = self.gg.get_github_query_result(query=query, per_page=query_number, page=page_number, order=order)
            for i in query_result:
                embed = Embed(title=f"**{i['name']}**", description=i['description'], color=0xff0000)
                embed.add_field(name="Owner : ", value=i['owner']['login'])
                embed.add_field(name="URL", value=i['html_url'], inline=False)
                embed.add_field(name="Watchers count", value=i['watchers_count'])
                embed.add_field(name="Language", value=i['language'])
                embed.add_field(name="Forks", value=i['forks_count'])
                embed.add_field(name="Open Issues count", value=i['open_issues_count'])
                await ctx.send(embed=embed)
                asyncio.sleep(1)

        @self.client.command()
        async def reddit_today(ctx):
            end = "-" * 156
            await ctx.send(f"Let's see what is on Reddit today!,<@{ctx.author.id}> ")

            try:
                posts = await self.reddit.recommend()
                for i in posts:
                    await ctx.send(f"# {' ' * 20}**{i['Title']}**{' ' * (30 - len(i['Title']))} #")
                    await ctx.send(f"# {' ' * 20}{i['Author']}{' ' * (30 - len(i['Title']))} #")  # Author with slightly larger size
                    await ctx.send(f"{i['Content'][:2000]}")
                    await ctx.send(f"{i['Media']} \n")
                    await ctx.send(f"{i['URL']}")
                    await ctx.send(f"{end}\n\n\n\n\n")
                    await asyncio.sleep(1)
            except Exception as e:
                await ctx.send(f"Ah, something went wrong, try again later,<@{ctx.author.id}>")

        @self.client.command()      
        async def reddit_toppost(ctx,subreddit:str,limit:int=5):
            if(len(subreddit)==0):
                await ctx.send(f"Type the name of the subreddit,<@{ctx.author.id}>")
            else:
                try:
                    posts = await self.reddit.top_post_subreddit(subreddit,limit=limit)
                    for i in posts:
                        embed = Embed(title=f"**{i['Title']}**", description=i['Content'][:2000], color=0x0000ff)
                        embed.add_field(name="Redditor", value=i['Author'])
                        embed.add_field(name="URL", value=i['URL'], inline=False)
                        embed.set_image(url=i['URL'])
                        embed.add_field(name="Score", value=i['Score'])
                        await ctx.send(embed=embed)
                        await asyncio.sleep(1)
                except Exception as e:
                    await ctx.send(f"You must have typed a wrong subreddit, or something went wrong either way try again later,<@{ctx.author.id}>")

    def run(self):
        self.client.run(self.token)

token = tokens.discord_token
bot = Vance(token)
bot.run()


