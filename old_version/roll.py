import discord
import re
import random

__max_rolls=20
__max_dice=100
__dice_colours={'green','lime','yellow','white','orange','red','black'}
__colour_rolls={
	'green': ['Small Fail','Big Success','Big Success','Big Success'],
	'lime': ['Fail','Success','Big Success','Big Success'],
	'yellow': ['Fail','Success','Success','Big Success'],
	'white': ['Big Fail','Fail','Success', 'Big Success'],
	'orange': ['Big Fail','Fail','Fail','Success'],
	'red': ['Big Fail','Big Fail','Fail','Success'],
	'black': ['Big Fail','Big Fail','Big Fail','Small Success']}
__duel_texts=["Let's get ready to RUMBLEEEEE!",
			  "It's duel time!",
			  "Time for some dueling!"]

#exceptions
class MultirollError(Exception):
	pass

class RollCommandError(Exception):
	pass

class DuelRollError(Exception):
	pass

async def init(message:discord.Message, command):
	no_of_rolls=0
	rolls=[]
	if not command: #check, if command string is empty
		await message.channel.send('No dice type selected, np. d10, d4 red')
		return
	if command[0].lower()=='duel':
		try:
			return_message=await duel_roll(message,command[1:])
		except DuelRollError:
			return
	elif command[0].lower()=='fate':
		return_message=await fate_roll(message)
	elif command[0].isdigit(): #Multiple dice rolls
		if int(command[0])<2 and int(command[0])>__max_rolls:
			await message.channel.send('Number of rolls must be between 2-'+str(__max_rolls))
			return
		try:
			return_message=await multi_roll(message,int(command[0]),command[1:])
		except MultirollError:
			return
	else:#'single' dice roll
		try:
			return_message,dump=await roll_dice(message,command)
		except RollCommandError:
			return
	print(len(return_message))
	await message.channel.send(message.author.name+" rolls:\n"+return_message)


async def multi_roll(message:discord.Message, n_of_rolls:int,command)->str:
	reply_message=""
	results=[]
	if not command:
		await message.channel.send('No dice type selected, ie. d10, d4 red')
		raise MultirollError
	if command[0].isnumeric():
		await message.channel.send('Too much numbers!')
		raise MultirollError
	try:
		for i in range(n_of_rolls):
			roll_message,result=await roll_dice(message,command)
			results.append(result)
			reply_message+=roll_message
			if i<n_of_rolls-1:
				reply_message+="\n"
	except RollCommandError:
		raise MultirollError
	if n_of_rolls>1:
		reply_message+="\nHighest result: "+str(max(results))+"\nLowest result: "+str(min(results))
	return reply_message

async def duel_roll(message:discord.Message,command)->str:
	return_message=""
	if not command:
		await message.channel.send('No dice type selected, ie. d10')
		raise DuelRollError
	if command[0].isdigit():
		await message.channel.send("First parameter of duel cannot be number only")
		raise DuelRollError
	try: #check if enough parameters was sent
		dump=command[0]
		dump=command[1]
	except IndexError:
		await message.channel.send("Not enough parameters sent, need 2 rolls, and optionally players")
		raise DuelRollError
	try:
		p1_message,result_p1=await roll_dice(message,[command[0]])
		p2_message,result_p2=await roll_dice(message,[command[1]])
	except RollCommandError:
		raise DuelRollError
	try:
		name_p1=command[2]
		name_p2=command[3]
	except IndexError:
		name_p1=""
		name_p2=""
	return_message=__duel_texts[random.randint(0,2)]+"\n"
	if name_p1 and name_p2:
		return_message+="   "+name_p1+" vs "+name_p2+"\n"
	if result_p1>result_p2:
		return_message+="   "+("  "*len(name_p1))+"__**"+str(result_p1)+"**__      "+str(result_p2)+"\n"
		if name_p1:
			return_message+=name_p1+" wins this duel"
	if result_p1<result_p2:
		return_message+="   "+("  "*len(name_p1))+str(result_p1)+"      __**"+str(result_p2)+"**__\n"
		if name_p2:
			return_message+=name_p2+" wins this duel"
	if result_p1==result_p2:
		return_message+="   "+str(result_p1)+"  "+str(result_p2)+"\nDraw!"

	if name_p1 and name_p2:
		return_message+="\n"+name_p1+"'s "+p1_message+"\n"+name_p2+"'s "+p2_message
	else:
		return_message+="\nFirst "+p1_message+"\nSecond "+p2_message
	return return_message

async def fate_roll(message):
	dump,roll=await roll_dice(message, ['d2'])
	if roll==1:
		return_message="Fortune is not in your favour :thumbsdown:"
	elif roll==2:
		return_message="Fortune is in your favour :thumbsup:"
	return return_message

async def roll_dice(message:discord.Message,command):
	colour_dice=False
	command[0].lower()
	if command[0].count('d') !=1 or re.search('[a-ce-z!@#$%^&(){}[]:~`";=_,.?/|]',command[0]):
		await message.channel.send('Roll command need to be ie. d4,5d8+2')
		raise RollCommandError
	if command[0][0]=='d':
		roll_command=command[0][1:]
		roll_count=1
	else:
		roll_count,roll_command=command[0].split('d')
		if not roll_count.isdigit():
			await message.channel.send('Roll command need to be ie. d4,5d8+2')
			raise RollCommandError
		roll_count=int(roll_count) #convert string to int
		if int(roll_count)>__max_rolls:
			await message.channel.send('Number of rolls must be between 2-'+str(__max_rolls))
			raise RollCommandError
	math_sym_count=roll_command.count('+')+roll_command.count('-')+roll_command.count('*')+roll_command.count('/')
	if '+' in roll_command:
		math_sym='+'
	if '-' in roll_command:
		math_sym='-'
	if '*' in roll_command:
		math_sym='*'
	if '/' in roll_command:
		math_sym='/'
	if math_sym_count==1:
		dice_size,roll_modifier=map(int,roll_command.split(math_sym))
	elif not math_sym_count:
		dice_size=int(roll_command)
	if dice_size>__max_dice or dice_size<2:
		await message.channel.send('Choose dice between 2-'+str(__max_dice))
		raise RollCommandError
	rolls=[random.randint(1,dice_size)for _ in range(roll_count)]
	rolls.sort(reverse=True)
	result=sum(rolls)
	if '+' in roll_command:
		result+=roll_modifier
	elif '-' in roll_command:
		result.sub(roll_modifier)#-=roll_modifier
	elif '*' in roll_command:
		result.mul(roll_modifier)#*=roll_modifier
	elif '/' in roll_command:
		result.div(roll_modifier)#=int(float(result)/float(roll_modifier))
	return_message=" "+str(rolls)
	try:
		if roll_count==1 and dice_size==4 and not math_sym_count and command[1] in __dice_colours:
			result_message=" Result: "+__colour_rolls[command[1]][rolls[0]-1]+" ("+command[1]+" dice)"
			colour_dice=True
	except IndexError:
		pass
	if not colour_dice:
		if roll_count>1 or math_sym_count>0:
			result_message=" Result: "+str(result)
		else:
			result_message=""
	return return_message+result_message,result