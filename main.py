import discord
import time
import asyncio
import os
import json
from discord.ext.commands.core import bot_has_guild_permissions 
from dotenv import load_dotenv
from discord import activity
from discord import permissions
from discord.ext import commands
from discord import client
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
from discord.utils import get

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import firestore

cred = credentials.Certificate('ServiceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()





intents = discord.Intents.default()
intents.members = True
intents.invites = True
load_dotenv()
client = commands.Bot(command_prefix=(os.environ['prefix']))


#   ELENCO CLASSI

class utils(object):
    def convert(string):
        list = string
        op = list.strip('][').split(', ')
        print(op)
        return op



# EVENTI
class events():
    @client.event
    async  def on_ready():
        print(client.user,"è ora Online")


    @client.event
    async def on_voice_state_update(member, before, after):
        class cache(object):
            key = ""
            guild = ""
        userid = member.id

        if before.channel == None:
            cache.guild = after.channel.guild.id
        if after.channel == None:
            cache.guild = before.channel.guild.id
        if after.channel != None and before.channel != None:
            cache.guild = before.channel.guild.id            
        print(cache.guild)
        result = db.collection('servers').document(str(cache.guild)).get()
        if result.exists:
            None
            bchannel = before.channel
            achannel =  after.channel
            docs = db.collection('servers').document(str(cache.guild)).collection('reactions').where("id","==",str(userid)).get()
       
            for doc in docs:
                key = (doc.id)
                cache.key = key
            if bchannel == None:
                db.collection('servers').document(str(cache.guild)).collection('reactions').document(cache.key).set({'channel': str(achannel.id)}, merge= True)
            if bchannel != None and achannel != None:
                aid = achannel.id
                if str(aid) != (db.collection('servers').document(str(cache.guild)).collection('reactions').document(cache.key).get()).get("channel"):               
                    await member.edit(voice_channel = bchannel)
            if achannel == None:
                db.collection('servers').document(str(cache.guild)).collection('reactions').document(cache.key).update({"channel": firestore.DELETE_FIELD})
                    
                
            if before and after != None:   
                try:
                    if before.channel.id != None and after.channel.id != None:
                        if before.channel.guild.id != after.channel.guild.id:
                            None
                except AttributeError:
                    None
        try:
            guild = after.channel.guild.id                
            if os.path.exists(f"{guild}/pv"):
                fopen = open(f"{guild}/pv/cache","r")
                read = fopen.read()
                list = read.split(", ")
                fopen.close()
                try:
                    while True:
                        name = list.pop()
                        if name != "":
                            file = open(f"{guild}/pv/{name}","r")
                            slist = file.read().split(", ")
                            if str(userid) in slist:
                                bid = slist.pop(0)
                                if str(achannel.id) == bid:
                                    achannelid = slist.pop(0)
                                    newchannel = client.get_channel(int(achannelid))
                                    await member.edit(voice_channel = newchannel)
                except IndexError:
                    None
        except AttributeError:
            None
            


    @client.event
    async def on_raw_reaction_add(payload):
        if payload.user_id != 990374263624183828:
            result = db.collection('servers').document(str(payload.guild_id)).get()
            if result.exists:
                None
            messageid = int(result.to_dict().get('messageid'))
            userslist = []
            if messageid != None:
                if int(payload.message_id) == messageid:
                    docs = db.collection('servers').document(str(payload.guild_id)).collection('reactions').get()
                    for doc in docs:
                        userslist.append(doc.to_dict().get("id"))
                    if str(payload.user_id) in userslist:
                        None
                    else:
                        db.collection('servers').document(str(payload.guild_id)).collection('reactions').add({"id":f"{payload.user_id}"})
    @client.event
    async def on_raw_reaction_remove(payload):
        if payload.user_id != 990374263624183828:        
            result = db.collection('servers').document(str(payload.guild_id)).get()
            if result.exists:
                None            
            messageid = int(result.to_dict().get('messageid'))
            docs = db.collection('servers').document(str(payload.guild_id)).collection('reactions').get()
            userslist = []
            for doc in docs:
                userslist.append(doc.to_dict().get("id"))

            if messageid != None:
                if int(payload.message_id) == messageid:
                    if str(payload.user_id) in userslist:
                        docs = db.collection('servers').document(str(payload.guild_id)).collection('reactions').where("id", "==", (str(payload.user_id))).get()
                        for doc in docs:
                            key = doc.id
                            db.collection('servers').document(str(payload.guild_id)).collection('reactions').document(key).delete()


   
# COMANDI
class commands():

    class tests():
        @client.command(name = "testing", description ="Server per testare quello che sto programmando")
        @has_permissions(administrator = True)
        async def _testing(ctx):
            print('hola')
            channel = ctx.channel
            lid = channel.last_message
            await asyncio.sleep(5)
            await lid.delete()
    class configs():
        @client.command(name = "configura", description ="Configura la chat per i logs e cosevarie")
        @has_permissions(administrator = True)
        async def _configura(ctx):
            guild = ctx.channel.guild
            result = db.collection('servers').document(str(guild.id)).get()
            bool = False
            if result.exists:
                if result.to_dict().get('channelid') != None:
                    await ctx.send(f"Bot già configurato in un canale. Per annullare la configurazione scrivi {os.environ['prefix']}deconf")
                else:
                    bool = True
            if result.exists == False or bool == True:
                discord.User = ctx.message.author
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(send_messages=False),
                }
                channel = await guild.create_text_channel('utility-bot', overwrites=overwrites)
                await ctx.channel.purge(limit=1)
                await channel.send("***FUNZIONI:***\n✅: ti riporta nel canale dove eri se vieni spostato ")
                msg = channel.last_message
                time.sleep(0.5)
                await msg.add_reaction("✅")
                data = {
                    "messageid": f'{msg.id}',
                    "channelid": f'{channel.id}'
                }
                db.collection('servers').document(str(guild.id)).set(data)
 
                
        @_configura.error
        async def configura_error(ctx, error):
            if isinstance(error, MissingPermissions):
                text = f"{ctx.message.author} non hai i permessi necessari"
                await ctx.send(text)

        @client.command(name = "confcheck", description ="Controlla che la configurazione sia corretta")
        @has_permissions(administrator = True)
        async def _confcheck(ctx):
            guild = ctx.channel.guild
            result = db.collection('servers').document(str(guild.id)).get()
            channelid = int(result.to_dict().get('channelid'))
            messageid = int(result.to_dict().get('messageid'))
            channel = guild.get_channel(channelid)
            await ctx.send(f"L'id del canale è {channel.id}, il nome del canale è {channel.name}.\nL'id del messaggio è {messageid}")
        @_confcheck.error
        async def confcheck_error(ctx, error):
            if isinstance(error, MissingPermissions):
                await ctx.send("Non hai i pemressi necessari per usare questo comando")

        @client.command(name = "deconf", description = "Cancella la configurazione del bot")
        @has_permissions(administrator = True)
        async def _deconf(ctx):
            guild = ctx.channel.guild
            result = db.collection('servers').document(str(guild.id)).get()
            if result.exists == False:
                await ctx.send(f"Il bot non è stato configurato. Configuralo scrivendo {os.environ['prefix']}configura nella chat dove vuoi configurarlo")     
            else:
                channelid = int(result.to_dict().get('channelid'))
                db.collection('servers').document(f'{guild.id}').update({"channelid": None})
                time.sleep(0.2)
                db.collection('servers').document(f'{guild.id}').update({'messageid': None})      
                channel = guild.get_channel(channelid)
                await channel.delete()  
                await ctx.send(f"Bot deconfigurato. Per configurarlo scrivi {os.environ['prefix']}configura  ")
        @_deconf.error
        async def deconf_error(ctx, error):
            if isinstance(error, MissingPermissions):
                text = f"{ctx.message.author} non hai i permessi necessari"
                await ctx.send(text)
                await ctx.send(text)
                channel = ctx.channel
                lid = channel.last_message
                await asyncio.sleep(10)
                await lid.delete()

    class utils():
        @client.command(name = "clear", description='Elimina messaggi [+clear + n.messaggi da eliminare]')
        @has_permissions(manage_messages=True, add_reactions = True)
        async def _clear(ctx, ammount=10000000000000000000000):
            #Elimina comodamente più messaggi. (+clear n. messaggi)
            discord.User = ctx.message.author
            if ammount == 10000000000000000000000:
                await ctx.send("Sicuro di voler eliminare tutti questi messaggi?")
                time.sleep(0.1)
                msg = ctx.channel.last_message
                await msg.add_reaction("✅")
                time.sleep(5)
                reactions = msg.reactions
                reaction = reactions.pop()
                users = await reaction.users().flatten()
                user = users.pop()
                if ctx.message.author == user:
                    print("Logico")
                    amm=ammount+1
                    await ctx.channel.purge(limit=amm)
                    await asyncio.sleep(0.5)
                    await ctx.send(f'messaggi eliminati: {ammount}')
                    lid2 = ctx.channel.last_message
                    time.sleep(2)
                    await lid2.delete()
                else:            
                    print("nope")
                    await msg.delete()
                    await ctx.send("Comando annullato")
                    time.sleep(0.2)
                    lid2 = ctx.channel.last_message
                    time.sleep(2)
                    await lid2.delete()
                    print("nope2")


            else:
                amm=ammount+1
                await ctx.channel.purge(limit=amm)
                await asyncio.sleep(0.5)
                await ctx.send(f'messaggi eliminati: {ammount}')
                lid = ctx.channel.last_message
                await asyncio.sleep(10)
                await lid.delete()   
        @_clear.error
        async def clear_error(ctx, error):
            if isinstance(error, MissingPermissions):
                text = f"{ctx.message.author} non hai i permessi necessari per eliminare i messaggi"
                await ctx.send(text)
                channel = ctx.channel
                lid = channel.last_message
                await asyncio.sleep(10)
                await lid.delete()

        @client.command(name = "delchannel", description="Elimina il canale specificato (ID). Se non viene specificato, elimina il canale corrente")
        @has_permissions(manage_channels=True)
        async def _delchannel(ctx, id=None):
            guild = ctx.channel.guild
            message = "Canale eliminato"
            if id == None: 
                channel = ctx.channel
                await channel.delete()
                await ctx.send(message)
            else: 
                channel = guild.get_channel(int(id))
                await channel.delete()
                await ctx.send(message)
            channel = ctx.channel
            lid = channel.last_message
            await asyncio.sleep(10)
            await lid.delete()
        @_delchannel.error
        async def delchannel_error(ctx, error):
            if isinstance(error, MissingPermissions):
                text = f"{ctx.message.author} non hai i permessi necessari per eliminare i canali"
                await ctx.send(text)
                channel = ctx.channel
                lid = channel.last_message
                await asyncio.sleep(10)
                await lid.delete()

        @client.command(name = "copychannel", description="Duplica il canale specificato (ID). Se non viene specificato, duplica il canale corrente")
        @has_permissions(manage_channels=True)
        async def _copychannel(ctx, id=None):
            guild = ctx.channel.guild
            message = ("Canale duplicato")
            if id == None: 
                channel = ctx.channel
                await channel.clone()
                await ctx.send(message)
            else: 
                channel = guild.get_channel(int(id))
                await channel.clone()
                await ctx.send(message)
            lid = channel.last_message
            await asyncio.sleep(10)
            await lid.delete()
        @_copychannel.error
        async def copychannel_error(ctx, error):
            if isinstance(error, MissingPermissions):
                text = f"{ctx.message.author} non hai i permessi necessari per duplicare i canali"
                await ctx.send(text)
                channel = ctx.channel
                lid = channel.last_message
                await asyncio.sleep(10)
                await lid.delete()
    class privatechannels(object):

        class locate():
            def before(ctx, nome):
                file = open(f"{ctx.channel.guild.id}/pv/{nome}","r")
                list = file.read().split(", ")
                bef = list.pop(0)
                print(bef)
            def after(ctx, nome):
                file = open(f"{ctx.channel.guild.id}/pv/{nome}","r")
                list = file.read().split(", ")
                bef = list.pop(1)
                print(bef)
            def user(ctx, nome):
                file = open(f"{ctx.channel.guild.id}/pv/{nome}","r")
                list = file.read().split(", ")
                bef = list.pop(2)
                print(bef)
            
        class cache():
            cache = []
            def update(id):
                print("Updating")
                file = open(f"{id}/pv/cache","r")
                split = file.read().split(", ")
                print(split)
                commands.privatechannels.cache.cache = split

        @client.command(name= "permit", description="Permette di spostare in automatico un utente in un canale privato. Struttura: before(opt.) ")
        @has_permissions(administrator = True)
        async def _permit(ctx, before, after, user: discord.User, nome):
            # avevo intenzione di creare una specie di sistema sfruttando sempre la cartella del server che si crea con configura
            # per fare in modo che ci siano delle specie di "combinazioni" tra canale di partenza e canale di arrivo e che sia tutto 
            # personalizzabile. Ovviamente richiederebbe un bel po' di lavoro, ma nulla che io non possa fare no?
            
            if nome == "cache":
                await ctx.send("Non puoi usare questo nome")
            else:
                if os.path.exists(f"{ctx.channel.guild.id}/pv") == False:
                    os.mkdir(f"{ctx.channel.guild.id}/pv")
                    open(f"{ctx.channel.guild.id}/pv/cache","w")
                
                file = open(f"{ctx.channel.guild.id}/pv/{nome}","w")
                cache = open(f"{ctx.channel.guild.id}/pv/cache","a")
                file.write(f'{before}, {after}, {user.id}')
                cache.write(f'{nome}, ')
                commands.privatechannels.cache.cache.append(nome)
                print(commands.privatechannels.cache.cache)


            

client.run(os.environ['token'])