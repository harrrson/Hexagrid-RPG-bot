import random
import re
import typing

from discord.ext import commands


async def _find_comment(text: str) -> str:
	return 'Comment: ' + text[text.find('!') + 1:] if '!' in text else ""


async def _split_roll_command(command: str):
	"""This function splits roll command into separate modifiers to use in roll function"""
	rolls_valid = False
	size_valid = False
	mod_valid = False
	rolls = 0
	dice_size = 0
	modifier = 0
	operator = ''

	command.lower()

	plus_count = command.count('+')
	minus_count = command.count('-')
	mul_count = command.count('*')
	div_count = command.count('/')

	if command.count('d') == 1 and (plus_count + minus_count + mul_count + div_count) < 2 and not re.search(
			'[a-ce-z!@#$%^&(){}[]:~`";=_,.?/|]', command):
		rolls, dice_size = command.split('d')
		if rolls.isdigit() or rolls == '':
			if rolls == '':
				rolls = 1
			else:
				rolls = int(rolls)
			rolls_valid = True
		if plus_count + minus_count + mul_count + div_count == 1:
			# only one of below variables can be one, so we got at max one character string
			operator = ('+' * plus_count) + ('-' * minus_count) + ('*' * mul_count) + ('/' * div_count)
			dice_size, modifier = dice_size.split(operator)
			if modifier == '':
				# modifier is 1 if we either multiply or divide, in other case is 0, and from upper condition, at max one can be 1
				modifier = mul_count + div_count
				mod_valid = True
			elif modifier.isdigit():
				modifier = int(modifier)
				mod_valid = True
		else:
			mod_valid = True
		if dice_size.isdigit():
			dice_size = int(dice_size)
			size_valid = True
	is_valid = size_valid and mod_valid and rolls_valid
	return is_valid, rolls, dice_size, modifier, operator


async def _roll(dice_size: int = 10, n_of_rolls: int = 1, roll_modifier: int = 0, roll_modifier_type: str = '+'):
	result = 0
	rolls = [random.randint(1, dice_size) for i in range(n_of_rolls)]
	rolls.sort(reverse=True)
	result = sum(rolls)
	if roll_modifier_type:
		if roll_modifier_type == '+':
			result = result + roll_modifier
		elif roll_modifier_type == '-':
			result = result - roll_modifier
		elif roll_modifier_type == '*':
			result = result * roll_modifier
		elif roll_modifier_type == '/':
			result = result / roll_modifier
	return rolls, result

#TODO: Modify text formatting, make rolls appear in frame
class Rolling(commands.Cog, name='Dice rolling'):
	__max_rolls = 30
	__max_dice = 100
	__dice_colours = ('green', 'lime', 'yellow', 'white', 'orange', 'red', 'black')
	__colour_rolls = {
		'green': ['Small Fail', 'Big Success', 'Big Success', 'Big Success'],
		'lime': ['Fail', 'Success', 'Big Success', 'Big Success'],
		'yellow': ['Fail', 'Success', 'Success', 'Big Success'],
		'white': ['Big Fail', 'Fail', 'Success', 'Big Success'],
		'orange': ['Big Fail', 'Fail', 'Fail', 'Success'],
		'red': ['Big Fail', 'Big Fail', 'Fail', 'Success'],
		'black': ['Big Fail', 'Big Fail', 'Big Fail', 'Small Success']
	}
	__duel_texts = [
		"Let's get ready to RUMBLEEEEE!",
		"It's duel time!",
		"Time for some dueling!"
	]

	def __init__(self, bot):
		self.bot = bot

	@commands.group(invoke_without_command=True, help='Roll dices depending of the parameters given')
	async def roll(self, ctx, rolls: typing.Optional[int] = 1, roll_command: str = 'd10', *, args=''):
		"""
		Rolling dice specified by user with modifiers
		:param ctx: discord.Context
		:param rolls: int [optional]
		:param roll_command: str
		:param args: str
		"""
		message = ['']
		roll_results = []
		if rolls > self.__max_rolls or rolls < 1:
			await ctx.send(f'You need to choose number of rolls between 1-{self.__max_rolls}')
			return
		valid_command, simult_rolls, dice_size, modifier, operator = await _split_roll_command(roll_command)
		if not valid_command:
			await ctx.send('Command is not valid.')
			return
		if operator == '/' and modifier == 0:
			await ctx.send('You cannot divide by 0.')
			return
		if simult_rolls > self.__max_rolls or simult_rolls < 1:
			await ctx.send(f'You need to choose number of rolls between 1-{self.__max_rolls}')
			return
		if dice_size < 2 or dice_size > self.__max_dice:
			ctx.send(f'You need to choose dice between 2-{self.__max_dice}')
		comment = await _find_comment(args)

		message[0] = f'{ctx.author.name}\'s rolls:'
		message_fragments_count = 0
		for i in range(rolls):
			roll_list, roll_result = await _roll(dice_size=dice_size, n_of_rolls=simult_rolls, roll_modifier=modifier,
			                                     roll_modifier_type=operator)
			roll_results.append(roll_result)
			roll_message = f'{roll_list}'
			if simult_rolls > 1 or operator:
				roll_message += f' Result {roll_result}'
			if len(message[message_fragments_count] + '\n' + roll_message) <= 2000:
				message[message_fragments_count] = message[message_fragments_count] + '\n' + roll_message
			else:
				message_fragments_count += 1
				message.append(roll_message)
		if rolls == 1:
			if len(message[message_fragments_count] + comment) <= 2000:
				message[message_fragments_count] = message[message_fragments_count] + comment
			else:
				message_fragments_count += 1
				message[message_fragments_count] = comment
		else:
			max_roll_message = f'\nHighest result: {max(roll_results)}'
			min_roll_message = f'\nLowest result: {min(roll_results)}'
			if len(message[message_fragments_count] + max_roll_message) <= 2000:
				message[message_fragments_count] += max_roll_message
			else:
				message_fragments_count += 1
				message[message_fragments_count] = max_roll_message
			if len(message[message_fragments_count] + min_roll_message) <= 2000:
				message[message_fragments_count] += min_roll_message
			else:
				message_fragments_count += 1
				message[message_fragments_count] = min_roll_message
			if len(message[message_fragments_count] + '\n' + comment) <= 2000:
				message[message_fragments_count] += '\n' + comment
			else:
				message_fragments_count += 1
				message[message_fragments_count] = comment
		for part_message in message:
			await ctx.send(part_message)

	@roll.command(name='duel', help='Makes a duel between two players, and shows a winner')
	async def duel(self, ctx, roll1='d10', roll2='d10', player1='Player 1', player2='Player 2', *, args=''):
		"""
		:param ctx: discord.Context
		:param roll1: str
		:param roll2: str
		:param player1: str
		:param player2: str
		:param args: str
		"""
		valid_command1, simult_rolls1, dice_size1, modifier1, operator1 = await _split_roll_command(roll1)

		valid_command2, simult_rolls2, dice_size2, modifier2, operator2 = await _split_roll_command(roll2)

		# Set of checks, if command is valid
		if not valid_command1 or not valid_command2:
			await ctx.send('Command is not valid.')
			return
		if (operator1 == '/' and modifier1 == 0) or (operator2 == '/' and modifier2 == 0):
			await ctx.send('You cannot divide by 0.')
			return
		if (simult_rolls1 > self.__max_rolls) or (simult_rolls1 < 1) or (simult_rolls2 > self.__max_rolls) or (
				simult_rolls2 < 1):
			await ctx.send(f'You need to choose number of rolls between 1-{self.__max_rolls}')
			return
		if dice_size1 < 2 or dice_size1 > self.__max_dice or dice_size2 < 2 or dice_size2 > self.__max_dice:
			ctx.send(f'You need to choose dice between 2-{self.__max_dice}')
		roll_list1, result1 = await _roll(dice_size1, simult_rolls1, modifier1, operator1)
		roll_list2, result2 = await _roll(dice_size2, simult_rolls2, modifier2, operator2)
		message = random.choice(self.__duel_texts) + '\n'
		if player1 and player2:
			message += f"   {player1} vs {player2}\n"
		if result1 > result2:
			message += "   " + ("  " * len(player1)) + "__**" + str(result1) + "**__      " + str(result2) + "\n"
			if player1:
				message += f"{player1} wins this duel"
		if result1 < result2:
			message += "   " + ("  " * len(player1)) + str(result1) + "      __**" + str(result2) + "**__\n"
			if player2:
				message += f"{player2} wins this duel"
		if result1 == result2:
			message += f"   {str(result1)}  {str(result2)}\nDraw!"
		if player1 and player2:
			message += f'\n{player1}\'s rolls: {roll_list1}'
			if simult_rolls1 > 1 or operator1:
				message += f' Result: {result1}'
			message += f'\n{player2}\'s roll: {roll_list2}'
			if simult_rolls2 > 1 or operator2:
				message += f' Result: {result2}'
		else:
			await ctx.send('Don\'t put empty strings when player names should be')
			# if result1 > result2 and not _counter:
			# 	message += "   " + ("  " * len(attacker_name)) + "__**" + str(result1) + "**__      " + str(
			# 		result2) + "\n"
			# 	if attacker_name:
			# 		message += attacker_name + " wins this duel"
			# if result1 < result2:
			# 	message += "   " + ("  " * len(attacker_name)) + str(result1) + "      __**" + str(result2) + "**__\n"
			# 	if defender_name:
			# 		message += defender_name + " wins this duel"
			# if result1 == result2:
			# 	message += "   " + str(result1) + "  " + str(result2) + "\nDraw!"
			# # If player names was given, write their names ad rolls
			# message += await _print_rolling_result(attacker_name, defender_name, result1, result2, roll_list1,
			#                                        roll_list2, simult_rolls1, simult_rolls2, operator1, operator2)
		await ctx.send(message)

	@roll.command(name='fate', help='Rolls two sided dice, and shows fate result depending on roll')
	async def fate(self, ctx, *, args: str = ''):
		result = random.randint(0, 1)
		comment = await _find_comment(args)
		if result:
			await ctx.send('Fate is on your side :thumbsup:' + comment)
		else:
			await ctx.send('Fate is not on your side :thumbsdown:' + comment)

	@roll.command(aliases=__dice_colours)
	async def _colour_roll(self, ctx, *, args: str = ''):
		comment = await _find_comment(args)
		result = random.choice(self.__colour_rolls[ctx.invoked_with])
		await ctx.send(f'{ctx.author.name}\'s roll: {result} ({ctx.invoked_with} dice)' + comment)


def setup(bot):
	bot.add_cog(Rolling(bot))
