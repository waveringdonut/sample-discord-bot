import discord
from discord import app_commands
from discord.ext import commands
import configparser
import random
import requests
import datetime
from discord import channel 
from discord import Member

# intentsをセットアップ
intents = discord.Intents.all()
intents.message_content = True  # メッセージコンテントのintentはオンにする
intents.members = True

# configをセットアップ
config_ini = configparser.ConfigParser()
config_ini.read('config.ini', encoding='utf-8')

# guild(Discordサーバー)の要素を持った配列を代入
MY_GUILDS = [discord.Object(id=config_ini.getint('GUILD', 'guild_id'))]

# MyClientクラスを定義
class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self) 
    async def setup_hook(self):
        for id in MY_GUILDS:
            self.tree.copy_global_to(guild=id)
            await self.tree.sync(guild=id)

# clientをセットアップ
client = MyClient(intents=intents)

# embedの関数を定義
def create_embed_roll_dies(name, num, icon_url):
    rolled_num =  random.randint(1, num)
    desc = f'You rolled **{rolled_num}**'

    # Embed関数でタイトル、説明、色を定義 
    embed = discord.Embed(title='',
                          description=desc,
                          color=0xffffff, 
                          )
    
    # set_author関数で名前とアイコンを定義
    embed.set_author(name=name, 
                     icon_url=icon_url 
                     )
    
    # 生成したembedを返す
    return embed

# embedの関数を定義
def create_embed_sushi(name, neta, icon_url):
    embed = discord.Embed(title='',
                          description=f'{neta}握り へいお待ち！',
                          color=0xffffff, 
                          )
    embed.set_author(name=name, 
                     icon_url=icon_url 
                     )
    return embed

# embedの関数を定義
def create_embed_menber(name, icon_url, member, channel):
    embed = discord.Embed(title='メンバー・チャンネル取得',
                          description=f'{member} {channel}',
                          color=0xffffff, 
                          )
    embed.set_author(name=name, 
                     icon_url=icon_url 
                     )
    return embed

# embedの関数を定義
def create_embed_roll_dies_info():
    embed = discord.Embed(title='?roll について',
                                description='',
                                color=0xffffff, 
                                )
    embed.add_field(name="説明",value="ダイスを振ります。\n [ダイスの目の数]は、d4, d6, d8, d10, d12, d20, d100 から選べます。")
    embed.add_field(name="使い方",value="?roll d[ダイスの目の数]")
    embed.add_field(name="使用例",value="?roll d4 \n ?roll d20 \n ?roll d100") 
    return embed

# botログイン完了時に実行
@client.event
async def on_ready(): 
    # ターミナルに送信
    print('ログインしました^^') 

# メッセージ送信を認識し実行
@client.event
async def on_message(message):

    # 送信者がbotの場合return
    if message.author == client.user: 
        return
    
    # 送信されたテキストチャンネルが特定のものでない場合return
    if int(message.channel.id) != config_ini.getint('CHANNEL', 'channel_id'):
        return
    
    # ?roll で始まるメッセージの場合
    if message.content.startswith('?roll'):
        num_list = [4, 6, 8, 10, 12, 20, 100]
        
        #ユーザのアイコンを取得
        avatar = message.author.display_avatar

        #ユーザのニックネームを取得
        name = message.author.display_name

        # try節を実行
        try :
            if message.content.startswith('?roll d'):

                # メッセージから数値を取得し代入
                num = int(message.content.split()[1][1:])

                if num in num_list:
                    
                    # embedを生成
                    embed = create_embed_roll_dies(name, num, avatar)
                    
                    print(f'{name}ダイスロール')
                else :
                    embed = create_embed_roll_dies_info() 
            else :
                embed = create_embed_roll_dies_info() 
        # エラーが起こった場合はexept節を実行
        except :
            embed = create_embed_roll_dies_info()
        # finally節を実行
        finally:
            await message.channel.send(embed=embed)

    # ! で始まるメッセージの場合
    elif message.content.startswith('!'):

        # !より後のテキストを送信
        await message.channel.send(message.content[1:])

    # こんにちは で始まるメッセージの場合
    elif message.content == 'こんにちは':
        await message.channel.send('こんにちは！')

    # 現在の時刻 で始まるメッセージの場合
    elif message.content == '現在の時刻':

        # 現在の時刻を取得
        dt_now = datetime.datetime.now().hour

        await message.channel.send(f'現在の時刻は{dt_now}時です。')

    # ID取得 で始まるメッセージの場合
    elif message.content == ('ID取得'):
        
        # ユーザIDを取得
        user_id = message.author.id

        await message.channel.send(f'あなたのユーザIDは {user_id} です。')

    # 今日の天気 で始まるメッセージの場合
    elif message.content == ('今日の天気'):

        # URLを宣言
        jma_url = "https://www.jma.go.jp/bosai/forecast/data/forecast/400000.json"

        # get関数でURLにGETリクエストを送信
        jma_res = requests.get(jma_url)
        
        # レスポンスをjsonに形式
        jma_json = jma_res.json()

        # 福岡の天気の要素を指定
        jma_weather = jma_json[0]["timeSeries"][0]["areas"][0]["weathers"][0]
        
        await message.channel.send(f'今日の福岡の天気は\n{jma_weather}')

    elif message.content == ('help'):
        embed = discord.Embed(title='サンプルbotが持つ機能の説明',
                          description='',
                          color=0xffffff, 
                          )
        embed.add_field(name="ダイス機能",value="入力：?roll d[数値]　結果：[数値]の面を持つダイスを振り出目を表示")
        embed.add_field(name="挨拶機能",value="入力：こんにちは　結果：こんにちは！と送信")
        embed.add_field(name="時刻機能",value="入力：現在の時刻　結果：現在の時刻を送信")
        embed.add_field(name="天気機能",value="入力：今日の天気　結果：今日の天気を送信")
        embed.add_field(name="ID取得機能",value="入力：ID取得　結果：ユーザIDを送信")
        embed.add_field(name="寿司握りコマンド",value="入力：/寿司握り　結果：コマンドで入力された引き数の寿司を握る")
        embed.add_field(name="member・channel取得コマンド",value="入力：/get_membar_channel　結果：引き数のメンバーとチャンネルを取得し送信(送信者にのみ表示)")

        
        await message.channel.send(embed = embed)

# client.tree.command関数で名前と説明を定義
@client.tree.command(name="寿司握り", 
                     description="botが寿司を握ります")

# commandの引き数とその説明を定義
@app_commands.describe(
    ネタ='寿司のネタを入力してください',
)

# test_commandを定義
async def test_command(interaction: discord.Interaction, ネタ: str):
    sushi_neta = ネタ
    avatar = interaction.user.display_avatar
    name = interaction.user.display_name
    embed = create_embed_sushi(name, sushi_neta, avatar)
    await interaction.response.send_message(embed = embed, ephemeral=False)

# client.tree.command関数で名前と説明を定義
@client.tree.command(name="get_membar_channel", 
                     description="サーバー内のメンバーとチャンネルを取得します")

# commandの引き数とその説明を定義
@app_commands.describe(
    メンバー1='1人目のメンバーを入力してください',
    チャンネル1='1つ目のチャンネルを入力してください',
)

# test_commandを定義
async def test_command2(interaction: discord.Interaction, メンバー1: discord.Member, チャンネル1: discord.abc.GuildChannel):
    members = メンバー1
    channels = チャンネル1
    avatar = interaction.user.display_avatar
    name = interaction.user.display_name
    embed = create_embed_menber(name, avatar, members, channels)
    await interaction.response.send_message(embed = embed, ephemeral=True)

# botが持つトークンで起動
client.run(config_ini.get('TOKEN', 'token')) 