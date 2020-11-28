import random
import re
import typing

from discord import Embed
from discord.ext import commands


async def _find_comment(text: str) -> str:
	max_len = 50
	if '!' in text:
		if len(text) - text.find('!') + 1 < max_len:
			return text[text.find('!') + 1:]
		else:
			return text[text.find('!') + 1:text.find('!') + max_len - 2] + '...'
	else:
		return ""


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


class Rolling(commands.Cog, name='Dice rolling'):
	__max_rolls = 20
	__max_dice = 100
	__dice_colours = ('green', 'lime', 'yellow', 'white', 'orange', 'red', 'black')
	__colour_rolls = {'green': ['Small Fail', 'Big Success', 'Big Success', 'Big Success'],
	                  'lime': ['Fail', 'Success', 'Big Success', 'Big Success'],
	                  'yellow': ['Fail', 'Success', 'Success', 'Big Success'],
	                  'white': ['Big Fail', 'Fail', 'Success', 'Big Success'],
	                  'orange': ['Big Fail', 'Fail', 'Fail', 'Success'],
	                  'red': ['Big Fail', 'Big Fail', 'Fail', 'Success'],
	                  'black': ['Big Fail', 'Big Fail', 'Big Fail', 'Small Success']
	                  }
	__duel_texts = ["Let's get ready to RUMBLEEEEE!", "It's duel time!", "Time for some dueling!"]

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
		roll_lists = []
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

		embed = Embed(title=f'Rolls for {ctx.author.display_name}', color=0xff0000, description=comment)
		for i in range(rolls):
			roll_list, roll_result = await _roll(dice_size=dice_size, n_of_rolls=simult_rolls, roll_modifier=modifier,
			                                     roll_modifier_type=operator)
			roll_results.append(roll_result)
			roll_lists.append(roll_list)
			field_rolls = f'{roll_list}'
			field_title = f'Roll #{i + 1}'
			if simult_rolls > 1 or operator:
				field_title += f': Result {roll_result}'
			embed.add_field(name=field_title, value=field_rolls, inline=True)
		if rolls > 1:
			embed.insert_field_at(index=0, name='Highest/lowest result',
			                      value=f'Highest result: {max(roll_results)}\nLowest result: {min(roll_results)}',
			                      inline=False)
		print(len(embed))
		await ctx.send(embed=embed)

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
		embed = Embed(title=f'Duel battle: {player1} VS {player2}', colour=0xff0000)
		embed.add_field(name=f'{player1}\'s roll', value=result1, inline=True)
		embed.add_field(name=f'{player2}\'s roll', value=result2, inline=True)
		# message = random.choice(self.__duel_texts) + '\n'
		if result1 > result2:
			embed.add_field(name=f'Winner:', value=player1, inline=False)
		elif result1 < result2:
			embed.add_field(name=f'Winner:', value=player2, inline=False)
		elif result1 == result2:
			embed.add_field(name=f'Draw!', inline=False)
		embed.add_field(name='Players\' rolls:', value=f'{player1}: {roll_list1}\n{player2}: {roll_list2}')
		await ctx.send(embed=embed)

	@roll.command(name='fate', help='Rolls two sided dice, and shows fate result depending on roll')
	async def fate(self, ctx, *, args: str = ''):
		comment = await _find_comment(args)
		embed = Embed(title=f'Fate roll for {ctx.author.display_name}', description=comment, color=0xff0000)
		if random.randint(0, 1):
			embed.add_field(name='Result', value='Fate is on your side :thumbsup:')
		else:
			embed.add_field(name='Result', value='Fate is not on your side :thumbsdown:')
		await ctx.send(embed=embed)

	@roll.command(aliases=__dice_colours)
	async def _colour_roll(self, ctx, *, args: str = ''):
		comment = await _find_comment(args)
		embed = Embed(title=f'Roll for {ctx.author.display_name}', color=0xff0000, description=comment)
		embed.add_field(name='Dice colour', value=ctx.invoked_with.lower(), inline=False)
		result = random.choice(self.__colour_rolls[ctx.invoked_with])
		embed.add_field(name='Result', value=result, inline=True)
		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Rolling(bot))
