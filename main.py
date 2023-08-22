import discord
from discord import app_commands
from discord.ext import commands
import configparser
import random
import requests

intents = discord.Intents.all()
intents.message_content = True  # メッセージコンテントのintentはオンにする
intents.members = True
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

MY_GUILDS = [discord.Object(id=config_ini.getint('GUILD', 'guild_id_ygm'))]

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self) 
    async def setup_hook(self):
        for id in MY_GUILDS:
            self.tree.copy_global_to(guild=id)
            await self.tree.sync(guild=id)

client = MyClient(intents=intents)

def create_embed_roll_dies(name, num, icon_url):
    rolled_num =  random.randint(1, num)
    desc = f'You rolled **{rolled_num}**' 
    embed = discord.Embed(title='',
                          description=desc,
                          color=0xffffff, 
                          )
    embed.set_author(name=name, 
                     icon_url=icon_url 
                     )
    return embed

def create_embed_sushi(name, neta, icon_url):
    embed = discord.Embed(title='',
                          description=str(neta)+'握りへいお待ち',
                          color=0xffffff, 
                          )
    embed.set_author(name=name, 
                     icon_url=icon_url 
                     )
    return embed

@client.event
async def on_ready(): #botログイン完了時に実行
    print('ログインしました^^') 

@client.event
async def on_message(message):
    if message.author == client.user: 
        return
    if int(message.channel.id) != config_ini.getint('CHANNEL', 'channel_id_ygm'):
        return
    if message.content.startswith('?roll'):
        r = '?roll d'
        num_list = [4, 6, 8, 10, 12, 20, 100]
        avatar = message.author.display_avatar
        name = message.author.display_name
        try :
            if message.content.startswith(r):
                num = int(message.content.split()[1][1:])
                if num in num_list:
                    embed = create_embed_roll_dies(name, num, avatar)
                    print(f'{name}ダイスロール')
                else :
                    embed = discord.Embed(title='?roll について',
                                description='',
                                color=0xffffff, 
                                )
                    embed.add_field(name="説明",value="ダイスを振ります。\n [ダイスの目の数]は、d4, d6, d8, d10, d12, d20, d100 から選べます。")
                    embed.add_field(name="使い方",value="?roll [ダイスの目の数]")
                    embed.add_field(name="使用例",value="?roll d4 \n ?roll d20 \n ?roll d100")   
        except :
            embed = discord.Embed(title='?roll について',
                                description='',
                                color=0xffffff, 
                                )
            embed.add_field(name="説明",value="ダイスを振ります。\n [ダイスの目の数]は、d4, d6, d8, d10, d12, d20, d100 から選べます。")
            embed.add_field(name="使い方",value="?roll [ダイスの目の数]")
            embed.add_field(name="使用例",value="?roll d4 \n ?roll d20 \n ?roll d100")
        finally:
            await message.channel.send(embed=embed)
    elif message.content == 'こんにちは':
        await message.channel.send('こんにちは！')
    elif message.content.startswith('!'):
        await message.channel.send(message.content[1:])
    elif message.content == ('?ID取得'):
        await message.channel.send(message.author.id)
    elif message.content == ('?天気'):
        jma_url = "https://www.jma.go.jp/bosai/forecast/data/forecast/400000.json"
        jma_json = requests.get(jma_url).json()
        jma_weather = jma_json[0]["timeSeries"][0]["areas"][0]["weathers"][0]
        await message.channel.send('今日の福岡の天気は\n' + str(jma_weather))

@client.tree.command(name="寿司握りコマンド", 
                     description="botが寿司を握ります")
@app_commands.describe(
    ネタ='寿司のネタを入力してください',
)
async def test_command2(interaction: discord.Interaction, ネタ: str):
    sushi_neta = ネタ
    avatar = interaction.user.display_avatar
    name = interaction.user.display_name
    embed = create_embed_sushi(name, sushi_neta, avatar)
    await interaction.response.send_message(embed = embed, ephemeral=False)

client.run(config_ini.get('TOKEN', 'token')) 