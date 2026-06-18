import time
import math
from decimal import Decimal, getcontext



class ArithmeticEncoder:
    def __init__(self, symbol_probabilities):
        self.symbol_probabilities = symbol_probabilities

    def encode(self, data):
        low = Decimal(0.0)
        high = Decimal(1.0)

        prec = math.ceil(len(data) * len(self.symbol_probabilities.keys()) * 0.13)
        if prec < 10000000000:
            getcontext().prec = prec
        else:
            getcontext().prec = 10000000000

        check = len(data)
        step = int(check / 100)


        if step <= 0:
            step = 1
        counter = 0
        for symbol in data:
            symbol_range = Decimal(high - low)
            high = low + symbol_range * self.symbol_probabilities[symbol][1]
            low = low + symbol_range * self.symbol_probabilities[symbol][0]

            counter += 1
            if counter % step == 0:
                percentage = int(counter / step) if int(counter / step) < 100 else 100

        result = (low + high) / Decimal(2.0)

        return result


class ArithmeticDecoder:
    def __init__(self, symbol_probabilities):
        self.symbol_probabilities = symbol_probabilities

    def decode(self, encoded_data, length):
        low = Decimal(0.0)
        high = Decimal(1.0)
        result = ""

        for _ in range(length):
            for symbol, (symbol_low, symbol_high) in self.symbol_probabilities.items():

                symbol_range = high - low
                symbol_low_in_range = Decimal(symbol_low) * symbol_range
                symbol_high_in_range = Decimal(symbol_high) * symbol_range

                if low + symbol_low_in_range <= encoded_data <= low + symbol_high_in_range:
                    result += symbol
                    high = low + symbol_range * symbol_high
                    low = low + symbol_range * symbol_low
                    break

        return result


def encode(string: str):
    letter_probabilities = {}

    for letter in string:
        if letter in letter_probabilities:
            letter_probabilities[letter] += 1
        else:
            letter_probabilities[letter] = 1

    letter_probabilities = dict(sorted(letter_probabilities.items(), key=lambda item: item[1], reverse=True))

    total_length = len(string)
    probabilities = {}
    low_range = Decimal(0.0)

    for letter, frequency in letter_probabilities.items():
        high_range = low_range + Decimal(frequency) / Decimal(total_length)
        probabilities[letter] = [low_range, high_range]
        low_range = Decimal(high_range)

    coder = ArithmeticEncoder(probabilities)
    result = {
        "code": str(coder.encode(string)),
        "probabilities": {key: str([float(num) for num in value]) for key, value in probabilities.items()},
        "length": len(string)
    }
    return result


def decode(number: float, length: int, probabilities: dict) -> str:
    decoder = ArithmeticDecoder(probabilities)

    return decoder.decode(number, length)





string = """Learn about chess vampires, an exciting concept relating chess, parity and math. Have you ever wondered how many legal positions exist in chess? Unfortunately, mankind is not ready to answer this eccentric question, although some estimations indicate that this number is comparable to the number of water molecules on Earth. However, there is a more reasonable target that we could aim for: is the number of legal positions even or odd? It turns out there exists a very convenient way of grouping positions in pairs, by pairing each position with its mirror image. Thus, could not we conclude that the number of legal positions is even? Not so quickly. There exist legal positions whose mirror image is illegal. Such positions without a mirror image are known as vampires, a fun term coined by Andrew Buchanan, who has studied this thrilling topic for several years and who introduced me to it. Mirror image of a position Legal positions First, let us clarify that a position is a configuration of pieces on the board (a diagram) together with the information of whose turn it is and what castling/en-passant rights are enabled. A position is said to be legal if it can be reached in an actual game. The most promising attempt of pairing positions is the following definition of mirror images. (Other efforts fall short, e.g., pairing positions with the same diagram and different turn leads to problems with checks, or a diagram reflection with respect to the vertical axis leads to castling issues, etc.) Definition of mirror image The mirror image of a position is the position obtained after reflecting the board configuration with respect to the horizontal axis in the center of the board, inverting the color of all pieces and inverting the turn (castling/en-passant rights are preserved, reflected). As an example, consider the starting position of the Spanish Opening and its mirror image, which is legal: it can be reached after e.g. 1. e3 e5 2. e4 Nf6 3. Nc3 Bb4. Note how we have moved the pawn to e4 in two steps in order to "lose a tempo". Starting position of the Spanish Opening (left) and its mirror image (right) Starting position of the Spanish Opening (left) and its mirror image (right) Vampires exist As we have anticipated, there exist legal positions with an illegal mirror image. In the rest of this post, I would like to help you discover that vampires exist by guiding you on how to find one. For that, we will leverage the following result. Every vampire comes from a vampire Exactly. Just as one would expect, vampires do not appear from thin air, they come from another "infected" individual. Formally, what this means is that all preceding positions to a vampiric position are vampires. In other words, if we make a retraction on a vampire, we reach another vampire. Proving this fact is not hard. Observe that by making a legal move on a non-vampiric position, we always reach a non-vampiric position. This is because the former position has a legal mirror image where we can make the analogous mirror move which leads to the (legal) mirror position that we wanted. Every legal move in a position has a corresponding move in its mirror image. Every legal move in a position has a corresponding move in its mirror image Can you now find a vampire? If every vampire comes from a vampire and under the assumption that vampires exist. Would you be able to find one? In other words, there are no vampires in the tree of variations that starts in a non-vampiric position. If vampires exist... The starting position must be a vampire! And, indeed, it is. If it were not a vampire, vampires would not exist. We can consider it the Head Vampire. But why is the starting position a vampire? The mirror image of the starting position is the same position with the turn inverted (Black to move). Such a position is in fact illegal because knights can only make even cycles, this makes it impossible to grant the turn to Black. In fact, all vampires are based on a parity argument of this kind. Only 1. a3, 1. f3, 1. h3 or knight moves preserve the parity invariant in the starting position Only 1. a3, 1. f3, 1. h3 or knight moves preserve the parity invariant in the starting position Challenge for the reader I invite you (in the same way Andrew invited me) to find a vampire where en-passant is possible. First, realize how hard it is to get a pawn advance without losing the parity invariant (a double pawn-push, e.g., loses the invariant because it allows for "triangulation", i.e. the pawn can push in two steps in the mirror image). Then, find a way to get to the 5th rank on a vampire. Now simply make a double pawn-push next to the pawn on the 5th rank. The en-passant flag will force the pawn to also push in one go in the mirror image, so you are good. Happy Halloween and good luck! We all know these days. You sleep badly, are sick, have a migraine, or have any other physical problem that makes you feel bad. But just on that day, you have an important chess game to play. What is the best way to go about that game? Should you change anything? This is the question I got from a reader not long ago. Sadly, I am quite experienced in playing games when not feeling great. Ever since my brain injury in 2017, I hardly had any games I really felt 100% fit. But I managed to find ways to get the most out of myself, even on bad days. This article should help you do the same. Before The Game If you still have some time before the game and realize it isn’t your game, there are some things you can do to increase the chance that you perform decently. As you already have limited energy, what you should avoid is a lengthy preparation. You simply can’t afford to lose any energy before the game! So forget about long opening preparation and do something good for your body. Everyone is different, so you will know best what helps your body recover on a given bad day. Additionally to your physical preparation, you need some mental adjustments. I have always been extremely ambitious, playing for a win with both colors against nearly any opponent. This strategy worked extremely well for me on decent days. But on the days I really felt bad, it was putting too much pressure on my weak body. Going for big complications wasn’t the smartest choice on such days. My key mantra on such days was “play in rapid mode.” It meant that I was aiming to play logical moves rather quickly. The goal wasn’t to find the most sophisticated lines but to keep the quality of each move on a decent level. Additionally, a relatively quick draw became a slight possibility for me on such days. I knew rationally that it might be the right choice to play it safe, get a draw, go home and recharge. Still, in practice, I nearly never got myself to do it. Just a few months after the brain injury, I got myself to make a move repetition against a strong GM with White and felt extremely bad afterward. Both physically because I was unable to sit straight on a chair without the feeling of falling over and mentally because I still felt bad about repeating moves on move 15. Especially as chess will be a hobby for most of you guys it simply isn’t worth it to jeopardize your health for a game of chess. Determine how bad the day really is and if playing a game of chess would make things worse or not. Depending on the answer, just play more cautiously, make an early draw, or forfeit the game and visit a doctor! During The Game If you find yourself playing a game and not feeling great, there are some small adjustments you can make to increase the quality of your moves. The key is to understand that you are playing below your normal strength and to accept that. You want to make the best out of the situation without expecting huge results. That means maybe not pushing as hard as you would on a normal day or opting for the same line instead of going for huge complications. But it also means that you really need all the energy you have left to be spent thinking about your moves. Depending on your energy, playing this game until the end might not have any additional learning benefit. In such cases, try to swallow your ego (which was hard for me) and accept draws against lower-rated opponents. This approach might save you a lot of pain and rating over time, especially when you play a tournament and have a round to play the next day. Playing Better When Feeling Sick Feeling a little unwell doesn’t always have to be bad, though. Sometimes I performed better than usual when I was sick with the flu. This made no sense until I realized I spent 100% of my energy thinking about chess if I was sick. On other days, I would walk around, talk to friends, watch other games, and think about dinner or a pretty girl. In other words: I wasted energy on many other things than thinking about my next move. When feeling sick, on the other hand, I somehow understood that this wasn’t possible. So I either tried to relax or think about the next moves. Using the full potential of my 80% capabilities on such days was more efficient than wasting 50% of my energy when feeling fully healthy. So, even feeling bad might not always be a disadvantage! Use it as a motivation to really think about the upcoming moves and take frequent breaks. How To Use “Rapid Game Mode” As mentioned above, the “rapid game mode” helped me make simple, logical decisions on such days. Especially when your head feels cloudy or slow, calculating long, difficult lines isn’t ideal. Usually, I’m a big fan of going for difficult lines, even if you can’t calculate them until the end. It is the only way to improve your skills in a tournament setting. But when you are feeling bad, the only thing you might learn is that you were feeling bad and thus missed a simple trick. Not a very fun way to spend your sick afternoon! So, opt for a logical game approach that does not need as much concrete calculation. And don’t spend your energy on decisions that won’t decide the game’s outcome. Without full energy, you don’t have the luxury of deciding which Rook you should put on the open line or if a subtlety will slightly improve your position. Go with what seems logical and don’t lose and save up the energy and time for more important decisions. When feeling bad, you might need double or triple the time to really calculate the game-deciding line. It would be a shame if you didn’t have that time and energy anymore because you wasted it on other things or less important chess decisions. 5 Steps To Better Results When Feeling Bad Improving your results on bad days will allow you to keep your rating floor higher than people that automatically give away points on bad days. Here is a step-by-step guide to what you should do: Avoid lengthy preparation on days you feel bad. Give your body time to relax and heal. For this day, all the energy left should be spent during the game. Change your mindset and expectations. On particularly bad days, allow yourself to offer quick draws or try a move repetition. Be careful not to use that as an easy excuse, though. I did that only when I couldn’t sit straight on my chair! Use all your energy for your chess decisions during the game. Avoid checking games of friends, saying hi to people, or thinking about anything other than chess. You need the remaining energy badly! Play “Rapid Game Mode,”Learn about chess vampires, an exciting concept relating chess, parity and math. Have you ever wondered how many legal positions exist in chess? Unfortunately, mankind is not ready to answer this eccentric question, although some estimations indicate that this number is comparable to the number of water molecules on Earth. However, there is a more reasonable target that we could aim for: is the number of legal positions even or odd? It turns out there exists a very convenient way of grouping positions in pairs, by pairing each position with its mirror image. Thus, could not we conclude that the number of legal positions is even? Not so quickly. There exist legal positions whose mirror image is illegal. Such positions without a mirror image are known as vampires, a fun term coined by Andrew Buchanan, who has studied this thrilling topic for several years and who introduced me to it. Mirror image of a position Legal positions First, let us clarify that a position is a configuration of pieces on the board (a diagram) together with the information of whose turn it is and what castling/en-passant rights are enabled. A position is said to be legal if it can be reached in an actual game. The most promising attempt of pairing positions is the following definition of mirror images. (Other efforts fall short, e.g., pairing positions with the same diagram and different turn leads to problems with checks, or a diagram reflection with respect to the vertical axis leads to castling issues, etc.) Definition of mirror image The mirror image of a position is the position obtained after reflecting the board configuration with respect to the horizontal axis in the center of the board, inverting the color of all pieces and inverting the turn (castling/en-passant rights are preserved, reflected). As an example, consider the starting position of the Spanish Opening and its mirror image, which is legal: it can be reached after e.g. 1. e3 e5 2. e4 Nf6 3. Nc3 Bb4. Note how we have moved the pawn to e4 in two steps in order to "lose a tempo". Starting position of the Spanish Opening (left) and its mirror image (right) Starting position of the Spanish Opening (left) and its mirror image (right) Vampires exist As we have anticipated, there exist legal positions with an illegal mirror image. In the rest of this post, I would like to help you discover that vampires exist by guiding you on how to find one. For that, we will leverage the following result. Every vampire comes from a vampire Exactly. Just as one would expect, vampires do not appear from thin air, they come from another "infected" individual. Formally, what this means is that all preceding positions to a vampiric position are vampires. In other words, if we make a retraction on a vampire, we reach another vampire. Proving this fact is not hard. Observe that by making a legal move on a non-vampiric position, we always reach a non-vampiric position. This is because the former position has a legal mirror image where we can make the analogous mirror move which leads to the (legal) mirror position that we wanted. Every legal move in a position has a corresponding move in its mirror image. Every legal move in a position has a corresponding move in its mirror image Can you now find a vampire? If every vampire comes from a vampire and under the assumption that vampires exist. Would you be able to find one? In other words, there are no vampires in the tree of variations that starts in a non-vampiric position. If vampires exist... The starting position must be a vampire! And, indeed, it is. If it were not a vampire, vampires would not exist. We can consider it the Head Vampire. But w"""
n = 0
while n >= 0:
    test_string = string[n:]

    start = time.time_ns()
    encode(string=test_string)
    finish = time.time_ns()

    print(f"{len(test_string)}: {(finish - start) / 10 ** 9}")
    with open("logs.txt", "a") as file:
        file.write(f"{len(test_string)}: {(finish - start) / 10 ** 9}\n")
    n += 500

