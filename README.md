# CoinBrawl - Bot

This is a bot to farm the [Coinbraw Bitcoin faucet](https://coinbrawl.com), it handles farming NPCs, upgrading stats and PVP automatically.

## Warning

#### This ~~may~~ will get you banned, user discretion advised!

### Usage

Clone or download as zip and modify the `config.ini` file to suit your needs, if you are farming stats remember to change the NPC id to one of the following number ids:

```
0 -> dummy: 0/0
1 -> village_idiot: 10/10
2 -> swordsman: 20/20
3 -> wandering_wizzard: 250/250
4 -> black_knight: 500/500
5 -> cyrstal_dragon: 1000/1000
```

Then run in a python enabled terminal:

```batch
python ./coinbrawl_bot.py -h, --help | -f, --farm-stats <stamina | tokens | attack | defense> | -p, --pvp <win_percentage>
```

Example usage:

You can run a farm npc/upgrade stamina routine by running:
```batch
python ./coinbrawl_bot.py --farm-stats stamina
```

Or farm all the available players against which you have 50% or more chance of winning:
```batch
python ./coinbrawl_bot.py -p 50
```

### Requirements:

 * Python 2.7+
 * fake_useragent 0.1.8
 * requests 2.18.4

### An important note about CoinBrawl and this bot

I made this bot mostly to see if I still remembered how to program in Python and so, it was made only for educational porpuses, also, please note that CoinBrawl seems to be abandoned. As currently, 12/26/2017, withdrawals are broken and that's one of the main reasons why I created this. It's not bad doing a bot for something that's not working anyways right?

### PVP warning

The script will battle all available players, notice that it will not reset the current amount of tokens available to battle those players, once you run out of tokens you must reset them manually.

### Copyright

License: GPL 2.0

Read file [COPYING](COPYING).
