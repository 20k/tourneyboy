import discord
import json
import sys 

client = discord.Client()

def read():
    with open('db.json', 'r') as content_file:
        return json.loads(content_file.read())
        
def read_file(x):
    with open(x, 'r') as content_file:
        return content_file.read()

def write(x):
    with open('db.json', 'w') as content_file:
        content_file.write(json.dumps(x))
        
def get_next_id(x):
    old = x["gid"]
    x["gid"] = x["gid"] + 1
    return old
    
def default_user_state(name, x):
    return {"name":name, "id":str(get_next_id(x)), "team":"", "elo":1200}
    
def get_user(id, x):
    return x["users"][id]
    
def get_elo(x):
    return x["elo"]
    
def get_expected_elo(my_elo, their_elo):
    return 1 / (1 + 10 ** ((their_elo - my_elo) / 400))
    
#my score is 1 for a victory, 0.5 for a tie, and 0 for a loss
def get_next_elo(my_elo, their_elo, my_score):
    return my_elo + 100 * (my_score - get_expected_elo(my_elo, their_elo))
    
def get_teams_info(x):
    teams = {}
    team_elo_total = {}
    
    for key, value in testdict["users"].items():
        if value["team"] in teams:
            teams[value["team"]].append(value["name"] + "#" + value["id"])
        else:
            teams[value["team"]] = [value["name"] + "#" + value["id"]]

        if value["team"] in team_elo_total:
            team_elo_total[value["team"]] += value["elo"]
        else:
            team_elo_total[value["team"]] = value["elo"]

    return {"teams":teams, "elo":team_elo_total}

def format_users(x):
    rval = ""
    for value in x:
        rval = rval + value + ","
        
    if len(rval) > 1:
        rval = rval[:-1]
        
    return rval
    
def format(in_val, all_vals):
    max_length = 0
    
    for value in all_vals:
        if len(value) > max_length:
            max_length = len(value)
            
    my_len = len(in_val)
    for i in range(my_len, max_length):
        in_val = in_val + " "
        
    return in_val

async def force_registration(message):
    backupcontent = message.content
    message.content = "!register"
    await on_message(message)
    message.content = backupcontent

testdict = read()

print(json.dumps(testdict))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
        
    user_header = "Name / Team / Elo\n"
        
    str_id = str(message.author.id)
    str_name = message.author.name;
    
    if message.content.startswith("!help"):
        await message.channel.send("```\n!register\n!unregister\n!players\n!join <teamname>\n!teams\n!victory <winningteam> <losingteam>\n!me\n!help```")
        
    if message.content.startswith("!me"):
        if str_id in testdict["users"]:
            value = testdict["users"][str_id]
            
            dnames = ["Team", value["team"]]
            dusers = ["Name", value["name"] + "#" + value["id"]]
            delo = ["Elo", str(round(value["elo"]))]
            
            formatted = "```"
            
            for i in range(0, len(dnames)):
                formatted = formatted + format(dusers[i], dusers) + " / " + format(dnames[i], dnames) + " / " + format(delo[i], delo) + "\n"
                    
            formatted = formatted + "```"            
            
            await message.channel.send(formatted)
            #await message.channel.send("```\n" + user_header + value["name"] + "#" + value["id"] + " / " + value["team"] + " / " + str(round(value["elo"])) + "```")
        else:
            await message.channel.send("Not found, !register first?")

    if message.content.startswith("!register"):
        if str_id not in testdict["users"]:
            testdict["users"][str_id] = default_user_state(str_name, testdict)
        else:
            testdict["users"][str_id]["name"] = str_name
            
        write(testdict)
        await message.channel.send('Registered User \"' + str_name + '\", your ID is ' + str(get_user(str_id, testdict)["id"]))
		
    if message.content.startswith('!quit'):
        sys.exit()
        
    if message.content.startswith('!players') or message.content.startswith('!list'):
        formatted = "```";
                
        elo_unsort = []
        
        dusers = ["Name"]
        dnames = ["Team"]
        delo = ["Elo"]
        
        for key, value in testdict["users"].items():
            elo_unsort.append(value)
            
        elo_sorted = sorted(elo_unsort, key=get_elo, reverse=True)
        
        for value in elo_sorted:
            #cur = value["name"] + "#" + value["id"] + " / " + value["team"] + " / " + str(round(value["elo"]))
            dusers.append(value["name"] + "#" + value["id"])
            dnames.append(value["team"])
            delo.append(str(round(value["elo"])))

        for i in range(0, len(dnames)):
            formatted = formatted + format(dusers[i], dusers) + " / " + format(dnames[i], dnames) + " / " + format(delo[i], delo) + "\n"
                    
        formatted = formatted + "```"            
        
        await message.channel.send(formatted)
        
    if message.content.startswith("!unregister"):
        if str_id in testdict["users"]:
            del testdict["users"][str_id]
            await message.channel.send("Goodbye! :)")
        else:
            await message.channel.send("Ur already ded 2 me")
        
        write(testdict)
        
    if message.content.startswith('!join '):
        post_split = message.content.split()
        
        if str_id not in testdict["users"]:
            await force_registration(message)
        
        if len(post_split) == 2:
            team_name = post_split[1]
                                
            testdict["users"][str_id]["team"] = team_name
            
            write(testdict)

            await message.channel.send('Joined ' + str_name + '#' + testdict["users"][str_id]["id"] + ' to team ' + team_name)
        else:
            await message.channel.send('!maketeam <single_word>')
            
    if message.content.startswith("!leave"):
        if str_id not in testdict["users"]:
            return
    
        testdict["users"][str_id]["team"] = ""
        write(testdict)

    if message.content.startswith('!teams'):
        formatted = "```"

        totals = get_teams_info(testdict)
        
        teams = totals["teams"]
        team_elo_total = totals["elo"]
   
        elo_unsort = []
        for key, value in teams.items():
            v = {}
            
            if key == "":
                continue
        
            v["users"] = value
            v["elo"] = team_elo_total[key]
            v["name"] = key;
        
            elo_unsort.append(v)
            
        elo_sorted = sorted(elo_unsort, key=get_elo, reverse=True)
        
        dnames = ["Team"]
        dusers = ["Members"]
        delo = ["Elo"]

        for value in elo_sorted:         
            dnames.append(value["name"])
            dusers.append(format_users(value["users"]))
            delo.append(str(round(value["elo"])))
                     
        for i in range(0, len(dnames)):
            formatted = formatted + format(dnames[i], dnames) + " / " + format(dusers[i], dusers) + " / " + format(delo[i], delo) + "\n"
            
        formatted = formatted + "```"
         
        await message.channel.send(formatted)

    if message.content.startswith("!victory "):
        post_split = message.content.split()
    
        if len(post_split) == 3:
            totals = get_teams_info(testdict)
            
            team_1 = post_split[1]
            team_2 = post_split[2]
            
            if team_1 == "" or team_2 == "":
                await message.channel.send("Nope")
                return
            
            if team_1 not in totals["elo"]:
                await message.channel.send("Team 1 is bad")
                return
            
            if team_2 not in totals["elo"]:
                await message.channel.send("Team 2 is bad")
                return
                
            if len(totals["teams"][team_1]) == 0 or len(totals["teams"][team_2]) == 0:
                await message.channel.send("No players in team")
                return

            elo_t1 = totals["elo"][team_1] / len(totals["teams"][team_1])
            elo_t2 = totals["elo"][team_2] / len(totals["teams"][team_2])
            
            for key, value in testdict["users"].items():
                if value["team"] == team_1:
                    value["elo"] = get_next_elo(value["elo"], elo_t2, 1)
                if value["team"] == team_2:
                    value["elo"] = get_next_elo(value["elo"], elo_t1, 0)
                    
            write(testdict)
            
            message.content = "!teams"
        
            await on_message(message)
        else:
            await message.channel.send("Usage: !victory <winner> <loser>")
        
            
client.run(read_file("./secret"))