from discord.ext import commands
from discord import Embed
import typing
import re
import random

rng_generator = random.SystemRandom()


class RollBaseException(Exception):
    pass


class WrongCommandFormula(RollBaseException):
    pass


class WrongDiceCount(RollBaseException):
    def __init__(self, dice_count):
        self.dice_count = dice_count


class WrongDiceSize(RollBaseException):
    def __init__(self, dice_size):
        self.dice_size = dice_size


class DivisionByZeroError(RollBaseException):
    pass


def _find_comment(text: str) -> str:
    max_len = 50
    if '!' in text:
        if len(text) - text.find('!') + 1 < max_len:
            return text[text.find('!') + 1:]
        else:
            return text[text.find('!') + 1:text.find('!') + max_len - 2] + '...'
    else:
        return ""


def _roll(dice_size=10, n_of_rolls=1, roll_modifier=0, roll_modifier_type='+'):
    rolls = [rng_generator.randint(1, dice_size) for _ in range(n_of_rolls)]
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


class Rolling(commands.Cog, name="Dice rolling."):
    _max_rolls = 20
    _dice_colours = ('green', 'lime', 'yellow', 'white', 'orange', 'red', 'black')
    _colour_rolls = {'green': ['Small Fail', 'Big Success', 'Big Success', 'Big Success'],
                     'lime': ['Fail', 'Success', 'Big Success', 'Big Success'],
                     'yellow': ['Fail', 'Success', 'Success', 'Big Success'],
                     'white': ['Big Fail', 'Fail', 'Success', 'Big Success'],
                     'orange': ['Big Fail', 'Fail', 'Fail', 'Success'],
                     'red': ['Big Fail', 'Big Fail', 'Fail', 'Success'],
                     'black': ['Big Fail', 'Big Fail', 'Big Fail', 'Small Success']
                     }

    def __init__(self, bot):
        self.bot = bot

    def _split_command(self, cmd):
        plus_count = cmd.count('+')
        minus_count = cmd.count('-')
        mul_count = cmd.count('*')
        div_count = cmd.count('/')
        # Check, if dice command have any unwanted parts
        if cmd.count('d') == 1 and cmd.count('e') <= 1 and (
                plus_count + minus_count + mul_count + div_count) < 2 and not re.search(
            '[a-cf-z!@#$%^&(){}[]:~`";=_,.?/|]', cmd):
            n_rolls, dice_size = cmd.split('d')
            # check, if roll count is an integer number, if not, command is wrong
            if n_rolls:
                try:
                    n_rolls = int(n_rolls)
                except ValueError:
                    raise WrongCommandFormula
            else:
                n_rolls = 1
            # check, if roll count is in valid range
            if n_rolls > self._max_rolls or n_rolls < 1:
                raise WrongDiceCount(n_rolls)
            try:
                # if dice size is integer number, work is over
                dice_size = int(dice_size)
                if dice_size < 2:
                    raise WrongDiceSize(dice_size)
                modifier = 0
                operator = '+'
                threshold = None
            except ValueError:
                # if not, check if user gives threshold value
                if dice_size.count('e') == 1:
                    # if yes, extract it from dice size
                    dice_size, threshold = dice_size.split('e')
                    # check, if threshold is float number
                    try:
                        threshold = float(threshold)
                        if threshold.is_integer():
                            threshold = int(threshold)
                    except ValueError:
                        raise WrongCommandFormula
                else:
                    threshold = None
                # Check again, if dice size is integer number (maybe threshold was problem earlier)
                try:
                    dice_size = int(dice_size)
                    if dice_size < 2:
                        raise WrongDiceSize(dice_size)
                    modifier = 0
                    operator = '+'
                except ValueError:
                    # If not, that means it can contain modifier
                    # only one of below variables can be one, so we got at max one character string
                    operator = ('+' * plus_count) + ('-' * minus_count) + ('*' * mul_count) + ('/' * div_count)
                    # check, if any math operator was found. If not, rolling formula is wrong
                    if not operator:
                        raise WrongCommandFormula
                    dice_size, modifier = dice_size.split(operator)
                    # Check once again,if dice size is integer number
                    try:
                        dice_size = int(dice_size)
                        if dice_size < 2:
                            raise WrongDiceSize(dice_size)
                    except ValueError:
                        # If not, give up and throw error
                        raise WrongCommandFormula
                    # Do the same to modifier, but cast it to float
                    try:
                        modifier = float(modifier)
                        if modifier.is_integer():
                            modifier = int(modifier)
                        if modifier == 0 and operator == '/':
                            raise DivisionByZeroError
                    except ValueError:
                        raise WrongCommandFormula

        else:
            raise WrongCommandFormula
        return n_rolls, dice_size, modifier, operator, threshold

    @commands.group(invoke_without_command=True, help='Roll dices depending of the parameters given')
    async def roll(self, ctx, rolls: typing.Optional[int] = 1, roll_command: str = 'd10', *,
                   args=''):
        over_threshold = 0
        roll_results = []
        if rolls > self._max_rolls or rolls < 1:
            await ctx.send(f'You need to choose number of rolls between 1-{self.__max_rolls}')
            return
        # try to split content of roll command
        try:
            simult_rolls, dice_size, modifier, operator, threshold = self._split_command(roll_command)
        except WrongCommandFormula:
            await ctx.send(f'Command is not valid: {roll_command}!')
            return
        except WrongDiceCount as e:
            await ctx.send(f'Wrong number of dices ({e.dice_count}), choose number between 1 and {self._max_rolls}!')
            return
        except WrongDiceSize as e:
            await ctx.send(f'Wrong dice size ({e.dice_count}), choose number greater than 1!')
            return
        except DivisionByZeroError:
            await ctx.send(f'Cannot divide by zero!')
            return

        comment = _find_comment(args)
        # prepare Embed frame
        embed = Embed(title=f'Rolls for {ctx.author.display_name}', color=0xff0000, description=comment)
        # roll dice
        for i in range(rolls):
            roll_list, roll_result = _roll(dice_size=dice_size, n_of_rolls=simult_rolls, roll_modifier=modifier,
                                           roll_modifier_type=operator)
            roll_results.append(roll_result)
            field_rolls = f'{roll_list}'
            field_title = f'Roll #{i + 1}'
            if simult_rolls > 1 or operator:
                field_title += f': Result {roll_result}'
            if threshold is None or roll_result >= threshold:
                if threshold is not None:
                    over_threshold += 1
                embed.add_field(name=field_title, value=field_rolls, inline=True)
        if rolls > 1:
            embed.insert_field_at(index=0, name='Highest/lowest result',
                                  value=f'Highest result: {max(roll_results)}\nLowest result: {min(roll_results)}',
                                  inline=False)
        if threshold is not None:
            embed.insert_field_at(index=1, name=f'Threshold value:{threshold}, passed:',
                                  value=f'{over_threshold}/{rolls}',
                                  inline=False)
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
        try:
            simult_rolls1, dice_size1, modifier1, operator1, threshold1 = self._split_command(roll1)

            simult_rolls2, dice_size2, modifier2, operator2, threshold2 = self._split_command(roll2)
        except WrongCommandFormula:
            await ctx.send(f'Command is not valid: {roll_command}!')
            return
        except WrongDiceCount as e:
            await ctx.send(f'Wrong number of dices ({e.dice_count}), choose number between 1 and {self._max_rolls}!')
            return
        except WrongDiceSize as e:
            await ctx.send(f'Wrong dice size ({e.dice_count}), choose number greater than 1!')
            return
        except DivisionByZeroError:
            await ctx.send(f'Cannot divide by zero!')
            return

        roll_list1, result1 = _roll(dice_size1, simult_rolls1, modifier1, operator1)
        roll_list2, result2 = _roll(dice_size2, simult_rolls2, modifier2, operator2)
        embed = Embed(title=f'Duel battle: {player1} VS {player2}', colour=0xff0000)
        embed.add_field(name=f'{player1}\'s roll', value=result1, inline=True)
        embed.add_field(name=f'{player2}\'s roll', value=result2, inline=True)
        if result1 > result2:
            embed.add_field(name=f'Winner:', value=player1, inline=False)
        elif result1 < result2:
            embed.add_field(name=f'Winner:', value=player2, inline=False)
        elif result1 == result2:
            embed.add_field(name=f'Draw!',value='No winner!', inline=False)
        embed.add_field(name='Players\' rolls:', value=f'{player1}: {roll_list1}\n{player2}: {roll_list2}')
        await ctx.send(embed=embed)

    @roll.command(name='fate', help='Rolls two sided dice, and shows fate result depending on roll')
    async def fate(self, ctx, *, args: str = ''):
        comment = _find_comment(args)
        embed = Embed(title=f'Fate roll for {ctx.author.display_name}', description=comment, color=0xff0000)
        if rng_generator.randint(0, 1):
            embed.add_field(name='Result', value='Fate is on your side :thumbsup:')
        else:
            embed.add_field(name='Result', value='Fate is not on your side :thumbsdown:')
        await ctx.send(embed=embed)

    @roll.command(aliases=_dice_colours)
    async def _colour_roll(self, ctx, rolls: typing.Optional[int] = 1, *, args: str = ''):
        if rolls < 1 or rolls > self._max_rolls:
            return await ctx.send(f'You need to choose number of rolls between 1-{self._max_rolls}')
        comment = _find_comment(args)
        embed = Embed(title=f'Roll for {ctx.author.display_name}', color=0xff0000, description=comment)
        embed.add_field(name='Dice colour', value=ctx.invoked_with.lower(), inline=False)
        if rolls == 1:
            embed.add_field(name='Result', value=rng_generator.choice(self._colour_rolls[ctx.invoked_with]),
                            inline=True)
        elif rolls > 1:
            for i in range(rolls):
                embed.add_field(name=f'Roll #{i + 1}', value=rng_generator.choice(self._colour_rolls[ctx.invoked_with]),
                                inline=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Rolling(bot))
