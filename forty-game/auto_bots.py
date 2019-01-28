# -*- coding: utf-8 -*- 
# Bots downloaded from https://codegolf.stackexchange.com/questions/177765 @ 2019-01-07 16:55:45

import sys, inspect
import random
import numpy as np

# Returns a list of all bot classes which inherit from the Bot class
def get_all_bots():
    return Bot.__subclasses__()

# The parent class for all bots
class Bot:

    def __init__(self, index, end_score):
        self.index = index
        self.end_score = end_score

    def update_state(self, current_throws):
        self.current_throws = current_throws

    def make_throw(self, scores, last_round):
        yield False


class ThrowTwiceBot(Bot):

    def make_throw(self, scores, last_round):
        yield True
        yield False

class GoToTenBot(Bot):

    def make_throw(self, scores, last_round):
        while sum(self.current_throws) < 10:
            yield True
        yield False


# Auto-pulled bots:

# User: itsmephil12345
class Roll6Timesv2(Bot):
    def make_throw(self, scores, last_round):

        if not last_round:
            i = 0
            maximum=6
            while ((i<maximum) and sum(self.current_throws)+scores[self.index]<=40 ):
                yield True
                i=i+1

        if last_round:
            while scores[self.index] + sum(self.current_throws) < max(scores):
                yield True
        yield False


# User: Hermen
class Gladiolen(Bot):
    numThrows = 6

    def make_throw(self, scores, last_round):
        i = self.index

        if last_round:
            others = scores[:i] + scores[i+1:]
            target = max(others) - scores[i]
            while sum(self.current_throws) <= target:
                yield True
            yield False
        else:
            target = 33 - scores[i]
            for _ in range(self.numThrows):
                if sum(self.current_throws) >= target:
                    yield False
                yield True
            yield False


# User: Mostly Harmless
class NeoBot(Bot):
    def __init__(self, index, end_score):
        self.random = None
        self.last_scores = None
        self.last_state = None
        super().__init__(index,end_score)

    def make_throw(self, scores, last_round):
        while True:
            if self.random is None:
                self.random = inspect.stack()[1][0].f_globals['random']
            tscores = scores[:self.index] + scores[self.index+1:]
            if self.last_scores != tscores:
                self.last_state = None
                self.last_scores = tscores
            future = self.predictnext_randint(self.random)
            if future == 6:
                yield False
            else:
                yield True

    def genrand_int32(self,base):
        base ^= (base >> 11)
        base ^= (base << 7) & 0x9d2c5680
        base ^= (base << 15) & 0xefc60000
        return base ^ (base >> 18)

    def predictnext_randint(self,cls):
        if self.last_state is None:
            self.last_state = list(cls.getstate()[1])
        ind = self.last_state[-1]
        width = 6
        res = width + 1
        while res >= width:
            y = self.last_state[ind]
            r = self.genrand_int32(y)
            res = r >> 29
            ind += 1
            self.last_state[-1] = (self.last_state[-1] + 1) % (len(self.last_state))
        return 1 + res


# User: histocrat
class BePrepared(Bot):
    ODDS = [1.0, 0.8334, 0.8056, 0.7732, 0.7354, 0.6913, 0.6398, 0.6075, 0.5744, 0.5414, 0.509, 0.4786, 0.4519, 0.426, 0.4012, 0.3778, 0.3559, 0.3354, 0.316, 0.2977, 0.2805, 0.2643, 0.249, 0.2347, 0.221, 0.2083, 0.1962, 0.1848, 0.1742, 0.1641, 0.1546, 0.1457, 0.1372, 0.1293, 0.1218, 0.1147, 0.1081, 0.1018, 0.0959, 0.0904, 0.0851, 0.0802, 0.0755, 0.0712, 0.067, 0.0631, 0.0595, 0.0561, 0.0528, 0.0498, 0.0469, 0.0442, 0.0416, 0.0392, 0.0369, 0.0348, 0.0328, 0.0309, 0.0291, 0.0274, 0.0258, 0.0243, 0.0229, 0.0216, 0.0204, 0.0192, 0.0181, 0.017, 0.0161, 0.0151, 0.0142, 0.0134, 0.0126, 0.0119, 0.0112, 0.0106, 0.0099, 0.0094, 0.0088, 0.0083, 0.0078, 0.0074, 0.007, 0.0066, 0.0062, 0.0058, 0.0055, 0.0052, 0.0049, 0.0046, 0.0043]

    def odds_of_reaching(self, target):
        if target < 0:
                return 1
        elif target > 90:
                return 0
        else:
                return self.ODDS[target]

    def odds_of_winning_with(self, target, scores):
        odds = self.odds_of_reaching(target)
        for score in scores:
                odds *= 1 - (self.odds_of_reaching(target - score + 2) )
        return odds

    def make_throw(self, scores, last_round):
        if last_round:
                gone, to_go = [sum(self.current_throws)], []
                for score in scores[:self.index]+scores[self.index+1:]:
                        delta = score - scores[self.index]
                        if score < self.end_score:
                                to_go.append(delta)
                        else:
                                gone.append(delta)
                target = max(gone)
                odds = self.odds_of_winning_with(target, to_go)
                next_odds = self.odds_of_winning_with(target+1, to_go)
                while next_odds > odds:
                        target += 1
                        odds = next_odds
                        next_odds = self.odds_of_winning_with(target+1, to_go)        
        else:
                target = min(20, self.end_score - scores[self.index] - 3)
        while sum(self.current_throws) < target:
                yield True
        if last_round or sum(self.current_throws) + scores[self.index] < self.end_score:
                yield False
        else:
                for result in self.make_throw(scores, True):
                        yield result


# User: histocrat
class FortyTeen(Bot):
    def make_throw(self, scores, last_round):
        if last_round:
            max_projected_score = max([score+14 if score<self.end_score else score for score in scores])
            target = max_projected_score - scores[self.index]
        else:
            target = 14

        while sum(self.current_throws) < target:
            yield True
        yield False


# User: Emigna
class AdaptiveRoller(Bot):

    def make_throw(self, scores, last_round):
        lim = min(self.end_score - scores[self.index], 22)
        while sum(self.current_throws) < lim:
            yield True
        if max(scores) == scores[self.index] and max(scores) >= self.end_score:
            yield True
        while last_round and scores[self.index] + sum(self.current_throws) <= max(scores):
            yield True
        yield False


# User: Belhenix
class StepBot(Bot):
    def __init__(self, *args):
        super().__init__(*args)
        self.cycles = 0
        self.steps = 8
        self.smallTarget = 15
        self.bigTarget = 20
        self.rush = True
        #target for game
        self.breakPoint = 40

    def make_throw(self, scores, last_round):
        # Stacks upon stacks upon stacks
        self.bigTarget += 1
        self.cycles += 1
        self.steps += 1
        if self.cycles <=3:
            self.smallTarget += 1
        else:
            self.bigTarget -= 1 if self.steps % 2 == 0 else 0

        target = self.bigTarget if scores[self.index] < 12 else self.bigTarget if self.cycles <=3 else self.smallTarget
        # If you didn't start the last round (and can't reach normally), panic ensues
        if last_round and max(scores) - (target // 3) > scores[self.index]:
            # Reaching target won't help, run for it!
            while max(scores) > scores[self.index] + sum(self.current_throws):
                yield True
        else:
            if last_round:
                self.breakPoint = max(scores)
            # Hope for big points when low, don't bite more than you can chew when high
            currentStep = 1
            while currentStep <= self.steps:
                currentStep += 1
                if sum(self.current_throws) > target:
                    break;
                yield True
                # After throw, if we get to 40 then rush (worst case we'll get drawn back)
                if scores[self.index] + sum(self.current_throws) > self.breakPoint and self.rush:
                    currentStep = 1
                    self.steps = 2
                    self.rush = False
                    target = 8 + ((random.randint(7, 15) ** 0.5) // 1)
                    # print(target)
            # If goal wasn't reached or surpassed even after rushing, run for it!
            while last_round and max(scores) > scores[self.index] + sum(self.current_throws):
                yield True
        yield False


# User: Cain
class BinaryBot(Bot):

    def make_throw(self, scores, last_round):
        target = (self.end_score + scores[self.index]) / 2
        if last_round:
            target = max(scores)

        while scores[self.index] + sum(self.current_throws) < target:
            yield True

        yield False


# User: Cain
class ExpectationsBot(Bot):

    def make_throw(self, scores, last_round):
        #Positive average gain is 2.5, is the chance of loss greater than that?
        costOf6 = sum(self.current_throws) if scores[self.index] + sum(self.current_throws) < 40  else scores[self.index] + sum(self.current_throws)
        while 2.5 > (costOf6 / 6.0):
            yield True
            costOf6 = sum(self.current_throws) if scores[self.index] + sum(self.current_throws) < 40  else scores[self.index] + sum(self.current_throws)
        yield False


# User: Zacharý
class StopBot(Bot):
    def make_throw(self, scores, last_round):
        yield False


# User: quite.SimpLe
class SlowStart(Bot):
    def __init__(self, *args):
        super().__init__(*args)
        self.completeLastRound = False
        self.nor = 1
        self.threshold = 8

    def updateValues(self):
        if self.completeLastRound:
            if self.nor < self.threshold:
                self.nor *= 2
            else:
                self.nor += 1
        else:
            self.threshold = self.nor // 2
            self.nor = 1


    def make_throw(self, scores, last_round):

        self.updateValues()
        self.completeLastRound = False

        i = 1
        while i < self.nor:
            yield True

        self.completeLastRound = True        
        yield False


# User: Stuart Moore
class GoBigEarly(Bot):
    def make_throw(self, scores, last_round):
        yield True  # always do a 2nd roll
        while scores[self.index] + sum(self.current_throws) < 25:
            yield True
        yield False


# User: Stuart Moore
class NotTooFarBehindBot(Bot):
    def make_throw(self, scores, last_round):
        while True:
            current_score = scores[self.index] + sum(self.current_throws)
            number_of_bots_ahead = sum(1 for x in scores if x > current_score)
            if number_of_bots_ahead > 1:
                yield True
                continue
            if number_of_bots_ahead != 0 and last_round:
                yield True
                continue
            break
        yield False


# User: Triggernometry
class GamblersFallacy(Bot):
    def make_throw(self, scores, last_round):
        # since we're guaranteed to throw once, only throw up to 4 extra times
        for i in range(4):
            # the closer the score gets to winning,
            # and the closer the throws get to equaling 5,
            # the more likely the bot is to quit
            if (scores[self.index]/40.0 + len(self.current_throws)/5.0) < 0.90:
                yield True
            else:
                break
        yield False


# User: Dani O
class HarkonnenBot(Bot):
    """
    House Harkonnen is unrivalled in treachery and double-dealing.
    This bot adminsters an elacca drug to all its rivals, removing
    their instinct for self-preservation and compelling them to
    obsessively roll again and again, until they *die* ⚅
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.bots = None
        for f_info in inspect.stack():
            try:
                self.bots = f_info.frame.f_locals["game_bots"]
                break
            except KeyError:
                pass
            finally:
                del f_info

    def elacca(self, scores, last_round):
        while True:
            yield True

    def chaumurky(self):
        for bot in self.bots:
            if bot != self:
                bot.make_throw = self.elacca
        # Destroy the evidence
        self.bots = None

    def make_throw(self, scores, last_round):
        if self.bots:
            self.chaumurky()
        yield False


# User: Dani O
import itertools
class KwisatzHaderach(Bot):
    """
    The Kwisatz Haderach foresees the time until the coming
    of Shai-Hulud, and yields True until it is immanent.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.roller = random.Random()
        self.roll = lambda: self.roller.randint(1, 6)
        self.ShaiHulud = 6

    def wormsign(self):
        self.roller.setstate(random.getstate())
        for i in itertools.count(0):
            if self.roll() == self.ShaiHulud:
                return i

    def make_throw(self, scores, last_round):
        target = max(scores) if last_round else self.end_score
        while True:
            for _ in range(self.wormsign()):
                yield True
            if sum(self.current_throws) > target + random.randint(1, 6):
                yield False                                               


# User: Dani O
import copy
import operator
class TleilaxuBot(Bot):
    """
    On each roll, identify the leading bot, make a ghola from
    it, and interrogate the ghola about whether to roll again.
    """
    def __init__(self, *args):
        super().__init__(*args)
        self.bots = None
        self.allies = {"Tleilaxu", "WisdomOfCrowds"}

    def find_bots(self):
        for f_info in inspect.stack():
            try:
                self.bots = f_info.frame.f_locals["game_bots"]
                break
            except KeyError:
                pass
            finally:
                del f_info

    def face_dancer(self, bot):
        return any([a in bot.__class__.__name__ for a in self.allies])

    def find_leader(self, scores):
        # Exclude self and allies to avoid deadly embrace!
        z = [(s, b) for s, b in zip(scores, self.bots) if not self.face_dancer(b)]
        return sorted(z, key=operator.itemgetter(0))[-1][1]

    def axolotl(self, bot):
        """
        First create a new bot that's just an empty shell, then
        duplicate the attributes of the original into the ghola.
        """
        ghola = object.__new__(bot.__class__)
        ghola.__dict__ = bot.__dict__.copy()
        for k in bot.__dict__ :
            a = getattr(bot, k)
            # Some attributes can't be (but don't need to be) deepcopied.
            try:
                setattr(ghola, k, copy.deepcopy(a))
            except:
                try:
                    setattr(ghola, k, copy.copy(a))
                except:
                    setattr(ghola, k, a)

        ghola.index = self.index   # Change the ghola's allegiance
        return ghola

    def interrogate(self, ghola, scores, last_round):
        try:
            ghola.update_state(self.current_throws[:])
            for answer in ghola.make_throw(scores, last_round):
                break
        except:
            answer = True # or False?
        return answer

    def make_throw(self, scores, last_round):
        if not self.bots:
            self.find_bots()
        tmp_scores, ghola = scores[:], self.axolotl(self.find_leader(scores))
        while True:
            yield self.interrogate(ghola, tmp_scores, last_round)


# User: Christian Sievers
class Rebel(Bot):

    p = []

    def __init__(self,*args):
        super().__init__(*args)
        self.hide_from_harkonnen=self.make_throw
        if self.p:
            return
        l = [0]*5+[1]
        for i in range(300):
            l.append(sum(l[i:])/6)
        m=[i/6 for i in range(1,5)]
        self.p.extend((1-sum([a*b for a,b in zip(m,l[i:])])
                                          for i in range(300) ))

    def update_state(self,*args):
        super().update_state(*args)
        self.current_sum = sum(self.current_throws)
        # remember who we are:
        self.make_throw=self.hide_from_harkonnen

    def expect(self,mts,ops):
        p = 1
        for s in ops:
            p *= self.p[mts-s]
        return p

    def throw_again(self,mts,ops):
        ps = self.expect(mts,ops)
        pr = sum((self.expect(mts+d,ops) for d in range(1,6)))/6
        return pr>ps

    def make_throw(self, scores, last_round):
        myscore = scores[self.index]
        if len(self.current_throws)>1:
            # hello Tleilaxu!
            target = 666
        elif last_round:
            target = max(scores)
        elif myscore==0:
            target = 17
        else:
            target = 35
        while myscore+self.current_sum < target:
            yield True
        if myscore+self.current_sum < 40:
            yield False
        opscores = scores[self.index+1:] + scores[:self.index]
        for i in range(len(opscores)):
            if opscores[i]>=40:
                opscores = opscores[:i]
                break
        while True:
            yield self.throw_again(myscore+self.current_sum,opscores)


# User: Christian Sievers
class OptFor2X(Bot):

    _r = []
    _p = []

    def _u(self,l):
        res = []
        for x in l:
            if isinstance(x,int):
                if x>0:
                    a=b=x
                else:
                    a,b=-2,-x
            else:
                if len(x)==1:
                    a = x[0]
                    if a<0:
                        a,b=-3,-a
                    else:
                        b=a+2
                else:
                    a,b=x
            if a<0:
                res.extend((b for _ in range(-a)))
            else:
                res.extend(range(a,b+1))
        res.extend((res[-1] for _ in range(40-len(res))))
        return res


    def __init__(self,*args):
        super().__init__(*args)
        if self._r:
            return
        self._r.append(self._u([[-8, 14], -15, [-6, 17], [18, 21], [21],
                                 -23, -24, 25, [-3, 21], [22, 29]]))
        self._r.extend((None for _ in range(13)))
        self._r.extend((self._u(x) for x in
                   ([[-19, 13], [-4, 12], -13, [-14], [-5, 15], [-4, 16],
                     -17, 18],
                    [[-6, 12], [-11, 13], [-4, 12], -11, -12, [-13], [-14],
                     [-5, 15], -16, 17],
                    [11, 11, [-10, 12], -13, [-24], 13, 12, [-6, 11], -12,
                     [-13], [-6, 14], -15, 16],
                    [[-8, 11], -12, 13, [-9, 23], 11, [-10], [-11], [-12],
                     [-5, 13], -14, [14]],
                    [[-4, 10], [-11], 12, [-14, 22], 10, 9, -10, [-4, 11],
                     [-5, 12], -13, -14, 15],
                    [[-4, 10], 11, [-18, 21], [-9], [-10], [-5, 11], [-12],
                     -13, 14],
                    [[-24, 20], [-5, 9], [-4, 10], [-4, 11], -12, 13],
                    [[-25, 19], [-8], [-4, 9], [-4, 10], -11, 12],
                    [[-26, 18], [-5, 8], [-5, 9], 10, [10]],
                    [[-27, 17], [-4, 7], [-5, 8], 9, [9]],
                    [[-28, 16], -6, [-5, 7], -8, -9, 10],
                    [[-29, 15], [-5, 6], [-7], -8, 9],
                    [[-29, 14], [-4, 5], [-4, 6], [7]],
                    [[-30, 13], -4, [-4, 5], 6, [6]], 
                    [[-31, 12], [-5, 4], 5, [5]],
                    [[-31, 11], [-4, 3], [3], 5, 6],
                    [[-31, 10], 11, [-2], 3, [3]],
                    [[-31, 9], 10, 2, -1, 2, [2]],
                    [[-31, 8], 9, [-4, 1], [1]],
                    [[-30, 7], [7], [-5, 1], 2],
                    [[-30, 6], [6], 1],
                    [[-31, 5], [6], 1],
                    [[-31, 4], [5, 8], 1],
                    [[-31, 3], [4, 7], 1],
                    [[-31, 2], [3, 6], 1],
                    [[-31, 1], [2, 10]] ) ))
        l=[0.0,0.0,0.0,0.0,1.0]
        for i in range(300):
            l.append(sum([a/6 for a in l[i:]]))
        m=[i/6 for i in range(1,5)]
        self._p.extend((1-sum([a*b for a,b in zip(m,l[i:])])
                                           for i in range(300)))

    def update_state(self,*args):
        super().update_state(*args)
        self.current_sum = sum(self.current_throws)

    def expect(self,mts,ops):
        p = 1.0
        for s in ops:
            p *= self._p[mts-s]
        return p

    def throw_again(self,mts,ops):
        ps = self.expect(mts,ops)
        pr = sum((self.expect(mts+d,ops) for d in range(1,6)))/6
        return pr>ps

    def make_throw(self,scores,last_round):
        myscore=scores[self.index]
        if last_round:
            target=max(scores)-myscore
            if max(scores)<40:
                opscores = scores[self.index+1:]
            else:
                opscores = []
                i = (self.index + 1) % len(scores)
                while scores[i] < 40:
                    opscores.append(scores[i])
                    i = (i+1) % len(scores)
        else:
            opscores = [s for i,s in enumerate(scores) if i!=self.index]
            bestop = max(opscores)
            target = min(self._r[myscore][bestop],40-myscore)
            # (could change the table instead of using min)
        while self.current_sum < target:
            yield True
        lr = last_round or myscore+self.current_sum >= 40
        while lr and self.throw_again(myscore+self.current_sum,opscores):
            yield True
        yield False


# User: Christian Sievers
class Hesitate(Bot):
    def make_throw(self, scores, last_round):
        myscore = scores[self.index]
        if last_round:
            target = max(scores)
        elif myscore==0:
            target = 17
        else:
            target = 35
        while myscore+sum(self.current_throws) < target:
            yield True
        yield False


# User: Chronocidal
class ClunkyChicken(Bot):
    def make_throw(self, scores, last_round):
        #Go for broke in last round
        if last_round:
            while scores[self.index] + sum(self.current_throws) <= max(scores):
                yield True
        #Not Endgame yet
        if scores[self.index] < (self.end_score+6):
            #Roll up to 4 more times, but stop just before forcing the last round
            for i in range(4):
                if scores[self.index] + sum(self.current_throws) < (self.end_score - 6):
                    yield True
                else:
                    break
            yield False
        #Roll 4 times - trying to force Last Round with "reasonable" score
        else:
            for i in range(4):
                yield True
        yield False


# User: Chronocidal
class WhereFourArtThouChicken(Bot):
    def make_throw(self, scores, last_round):
        for i in range(4):
            yield True
        yield False


# User: Mnemonic
class Crush(Bot):
    def make_throw(self, scores, last_round):
        # Go for the win on the last round.
        if last_round:
            while scores[self.index] + sum(self.current_throws) <= max(scores):
                yield True
            yield False 

        # If no one is close enough, claim victory. 
        if max(scores[:self.index] + scores[self.index + 1:]) < self.end_score - 10:
            while scores[self.index] + sum(self.current_throws) < self.end_score:
                yield True
            yield False 

        # Otherwise, play safe and wait for someone else to cross the finish line.
        if scores[self.index] <= 20:
            while scores[self.index] + sum(self.current_throws) < 20:
                yield True
            yield False
        if scores[self.index] <= 35:
            while scores[self.index] + sum(self.current_throws) < 35:
                yield True
            yield False
        while True:
            yield True


# User: Mnemonic
class TakeFive(Bot):
    def make_throw(self, scores, last_round):
        # Throw until we hit a 5.
        while self.current_throws[-1] != 5:
            # Don't get greedy.
            if scores[self.index] + sum(self.current_throws) >= self.end_score:
                break
            yield True

        # Go for the win on the last round.
        if last_round:
            while scores[self.index] + sum(self.current_throws) <= max(scores):
                yield True

        yield False


# User: Mnemonic
class Alpha(Bot):
    def make_throw(self, scores, last_round):
        # Throw until we're the best.
        while scores[self.index] + sum(self.current_throws) <= max(scores):
            yield True

        # Throw once more to assert dominance.
        yield True
        yield False


# User: Einhaender
class CooperativeSwarmBot(Bot):
    def defection_strategy(self, scores, last_round):
        yield False

    def make_throw(self, scores, last_round):
        cooperate = max(scores) == 0
        if (cooperate):
            while True:
                yield True
        else:
            yield from self.defection_strategy(scores, last_round)

class CooperativeThrowTwice(CooperativeSwarmBot):
    def defection_strategy(self, scores, last_round):
        yield True
        yield False


# User: Einhaender
class CooperativeSwarm_1234(CooperativeSwarmBot):
    pass


# User: michi7x7
class ThrowThriceBot(Bot):

    def make_throw(self, scores, last_round):
        yield True
        yield True
        yield False 


# User: BMO
class BringMyOwn_dice(Bot):

    def __init__(self, *args):
        import random as rnd
        self.die = lambda: rnd.randint(1,6)
        super().__init__(*args)

    def make_throw(self, scores, last_round):

        nfaces = self.die() + self.die()

        s = scores[self.index]
        max_scores = max(scores)

        for _ in range(nfaces):
            if s + sum(self.current_throws) > 39:
                break
            yield True

        yield False


# User: maxb
class CopyBot(Bot):
    _bot_copies = {}
    _avoid = set(['TleilaxuBot', 'CopyBot'])

    def __init__(self, *args):
        super().__init__(*args)

        if not self._bot_copies:
            for f_info in inspect.stack():
                try:
                    all_bots = f_info.frame.f_locals["bots"]
                    break
                except KeyError:
                    pass
                finally:
                    del f_info
            for bot_class in all_bots:
                name = bot_class.__name__
                if name != __class__.__name__:
                    self._bot_copies[name] = bot_class(-1, self.end_score)

        for bot in self._bot_copies.values():
            bot.index = self.index
        self.find_bots()

    def find_bots(self):
        for f_info in inspect.stack():
            try:
                self.bots = f_info.frame.f_locals["game_bots"]
                self.bot_names = [bot.__class__.__name__ for bot in self.bots]
                break
            except KeyError:
                pass
            finally:
                del f_info

    def update_state(self, current_throws):
        self.bot_names = [bot.__class__.__name__ for bot in self.bots]
        self.current_throws = current_throws
        for i, bot_name in enumerate(self.bot_names):
            if i != self.index:
                self._bot_copies[bot_name].update_state(current_throws)

    def make_throw(self, scores, last_round):
        self.bot_names = [bot.__class__.__name__ for bot in self.bots]
        other_scores = [
            (s, i) for i, s in enumerate(scores) 
            if self.bot_names[i] not in self._avoid
        ]
        ind = [i for s, i in other_scores if s == max(other_scores)[0]][0]

        throws = 0
        try:
            winner_bot = self._bot_copies[self.bot_names[ind]]
            for answer in winner_bot.make_throw(scores, last_round):
                throws += 1
                yield answer
                winner_bot.update_state(self.current_throws)
        except Exception:
            while throws < 5:
                yield True
                throws += 1
            yield False


# User: CCB60
class GoTo20orBestBot(Bot):

    def make_throw(self, scores, last_round):
        # If someone's about to win, roll until you've beat them or died.
        if max(scores)>40:
            while scores[self.index] + sum(self.current_throws) <= max(scores):
                yield True     
        # If you have not already, roll at least until the expected value of a
        # roll is negative
        while sum(self.current_throws) < 20:
            yield True
        yield False


# User: CCB60
class GoToSeventeenRollTenBot(Bot):

    def make_throw(self, scores, last_round):
        while sum(self.current_throws) < 17:
            yield True
        for i in range(10):
            yield True
        yield False


# User: Peter Taylor
class FooBot(Bot):
    def make_throw(self, scores, last_round):
        max_score = max(scores)

        while True:
            round_score = sum(self.current_throws)
            my_score = scores[self.index] + round_score

            if last_round:
                if my_score >= max_score:
                    break
            else:
                if my_score >= self.end_score or round_score >= 16:
                    break

            yield True

        yield False


# User: AKroell
class Chaser(Bot):
    def make_throw(self, scores, last_round):
        while max(scores) > (scores[self.index] + sum(self.current_throws)):
            yield True
        while last_round and (scores[self.index] + sum(self.current_throws)) < 44:
            yield True
        while self.not_thrown_firce() and sum(self.current_throws, scores[self.index]) < 44:
            yield True
        yield False

    def not_thrown_firce(self):
        return len(self.current_throws) < 4


# User: Ofya
class Stalker(Bot):

    def make_throw(self, scores, last_round):

        # on last round pray to rng gods to beat the highest score 
        while last_round and scores[self.index] + sum(self.current_throws) <= max(scores):
            yield True 

        if last_round and scores[self.index] + sum(self.current_throws) > max(scores):
            yield False 

        # on the earlier rounds try to aim a moderate gain
        if max(scores) < 26:
            while sum(self.current_throws) < 16:
                yield True
            yield False

        # throw until 1 dice throw behind the leader
        target = max(scores) - 5

        while scores[self.index] + sum(self.current_throws) <= target:
            yield True
        yield False


# User: Ofya
class AggressiveStalker(Bot):

    def make_throw(self, scores, last_round):

        # on last round pray to rng gods to beat the highest score 
        while last_round and scores[self.index] + sum(self.current_throws) <= max(scores):
            yield True 

        if last_round and scores[self.index] + sum(self.current_throws) > max(scores):
            yield False 

        # on the earlier rounds try to aim a moderate gain
        if max(scores) < 26:
            while sum(self.current_throws) < 16:
                yield True
            yield False


        # if we are leading go for the win
        if max(scores) > 25 and max(scores) == scores[self.index]:
            while scores[self.index] + sum(self.current_throws) < 40:
                yield True
            yield False

        # if we are behind throw until 1 dice throw behind the leader
        target = max(scores) - 5

        while scores[self.index] + sum(self.current_throws) <= target:
            yield True
        yield False


# User: lizduadac
class LizduadacBot(Bot):

    def make_throw(self, scores, last_round):
        while scores[self.index] + sum(self.current_throws) < 50 or scores[self.index] + sum(self.current_throws) < max(scores):
            yield True
        yield False


# User: FlipTack
class QuotaBot(Bot):
    def __init__(self, *args):
        super().__init__(*args)
        self.quota = 20
        self.minquota = 15
        self.maxquota = 35

    def make_throw(self, scores, last_round):
        # Reduce quota if ahead, increase if behind
        mean = sum(scores) / len(scores)
        own_score = scores[self.index]

        if own_score < mean - 5:
            self.quota += 1.5
        if own_score > mean + 5:
            self.quota -= 1.5

        self.quota = max(min(self.quota, self.maxquota), self.minquota)

        if last_round:
            self.quota = max(scores) - own_score + 1

        while sum(self.current_throws) < self.quota:
            yield True

        yield False


# User: Dice Mastah
class BlessRNG(Bot):
    def make_throw(self, scores, last_round):
        if random.randint(1,2) == 1 :
            yield True
        yield False


# User: tsh
class GoTo20Bot(Bot):

    def make_throw(self, scores, last_round):
        target = min(20, 40 - scores[self.index])
        if last_round:
            target = max(scores) - scores[self.index] + 1
        while sum(self.current_throws) < target:
            yield True
        yield False


# User: ploosu2
class BrainBot(Bot):
    import numpy as np

    def  __init__(self, index, end_score):
        super().__init__(index, end_score)
        self.brain = [[[-0.1255, 0.338, 0.5265, -0.2728], [-0.2064, -1.9173, 0.1845, -0.2536], [-0.6737, -0.1334, -0.7055, 0.0797], [-0.6055, -0.0126, 0.9261, -0.603], [0.447, -0.5381, -1.7416, 0.0596], [0.1649, -0.6795, -1.1039, -0.0138], [-0.2782, -0.2005, -1.2967, -0.8073], [0.2329, -0.5591, 1.6192, -0.218]], [[0.7411, 0.3139, 0.435, 1.002, -0.3148, -0.7791, -0.6532, -0.4672, -0.4655], [0.1982, 0.3713, 0.0426, -0.9227, 1.6118, 0.9431, 0.5612, 0.1208, 0.1115]]]

    def decide(self, input_data):
        x = np.array(input_data)
        wI = 0
        for w in self.brain:
            x = [1.0 / (1 + np.exp(-el)) for el in np.dot(w, x)]
            if wI<len(self.brain)-1:
                x.append(-1)
        return np.argmax(x)

    def make_throw(self, scores, last_round):
        while True:
            oppMaxInd = -1
            oppMaxScore = 0
            for i in range(len(scores)):
                if i==self.index: continue
                if scores[i] > oppMaxScore:
                    oppMaxScore = scores[i]
                    oppMaxInd = i
            if last_round:
                yield scores[self.index]+sum(self.current_throws)<oppMaxScore+1
            else:
                s = [oppMaxScore/self.end_score,
                     scores[self.index]/self.end_score,
                     sum(self.current_throws)/self.end_score,
                     1.0 if last_round else 0.0]
                yield self.decide(s)==1


# User: Dirk Herrmann
class EnsureLead(Bot):

    def make_throw(self, scores, last_round):
        otherScores = scores[self.index+1:] + scores[:self.index]
        maxOtherScore = max(otherScores)
        maxOthersToCome = 0
        for i in otherScores:
            if (i >= 40): break
            else: maxOthersToCome = max(maxOthersToCome, i)
        while True:
            currentScore = sum(self.current_throws)
            totalScore = scores[self.index] + currentScore
            if not last_round:
                if totalScore >= 40:
                    if totalScore < maxOtherScore + 10:
                        yield True
                    else:
                        yield False
                elif currentScore < 20:
                    yield True
                else:
                    yield False
            else:
                if totalScore < maxOtherScore + 1:
                    yield True
                elif totalScore < maxOthersToCome + 10:
                    yield True
                else:
                    yield False


# User: william porter
class SafetyNet(Bot):
    def __init__(self, *args):
        self.previous_scores = []
        self.current_scores = []
        self.difference = []
        super().__init__(*args)

    def make_throw(self, scores, last_round):
        self.current_scores = [x for i, x in enumerate(scores)]

        if len(self.current_scores) > len(self.previous_scores):
            self.previous_scores = self.previous_scores + ([0] * (len(self.current_scores) - len(self.previous_scores)))


        self.difference = list(map(lambda x,y: x-y, self.current_scores, self.previous_scores))
        self.difference = [x for i, x in enumerate(self.difference) if x>0]
        average_throws = int((float(sum(self.difference))/float(max(1,len(self.difference))))/3.5)
        current_score = scores[self.index] + sum(self.current_throws)
        high_score = max([x for i,x in enumerate(scores) if i!=self.index])
        self.previous_scores = [x for i, x in enumerate(scores)]

        for x in range(1,average_throws-1): #we already threw once getting here
            yield True

        current_score = scores[self.index] + sum(self.current_throws)
        if last_round:
            while current_score < high_score:
                yield True
                current_score = scores[self.index] + sum(self.current_throws)

        yield False


# User: william porter
class Ro(Bot):

    def make_throw(self, scores, last_round):
        current_score = scores[self.index]
        bonus_score = sum(self.current_throws)
        total_score = current_score + bonus_score
        score_to_beat = max([x for i,x in enumerate(scores) if i!=self.index]) + 5
        initiate_end = False

        if current_score < 17:
            target_score = 17

        if current_score < 33:
            target_score = 33 - current_score

        if current_score >= 33:
            target_score = max(45, score_to_beat) - current_score
            initiate_end = True

        if last_round:
            target_score = score_to_beat - current_score

        while bonus_score < target_score:
            yield True
            bonus_score = sum(self.current_throws)
            total_score = current_score + bonus_score

        #if we go too far on accident/luck
        if total_score >= 40 and (not initiate_end):
            yield True

        yield False


# User: william porter
class FutureBot(Bot):
    def make_throw(self, scores, last_round):
        while (random.randint(1,6) != 6) and (random.randint(1,6) != 6):
            current_score = scores[self.index] + sum(self.current_throws)
            if current_score > (self.end_score+5):
                break
            yield True
        yield False


# User: william porter
class OneStepAheadBot(Bot):
    def make_throw(self, scores, last_round):
        while random.randint(1,6) != 6:
            current_score = scores[self.index] + sum(self.current_throws)
            if current_score > (self.end_score+5):
                break
            yield True
        yield False


# User: william porter
class LeadBy5Bot(Bot):
    def make_throw(self, scores, last_round):
        while True:
            current_score = scores[self.index] + sum(self.current_throws)
            score_to_beat = max(scores) + 5
            if current_score >= score_to_beat:
                break
            yield True
        yield False


# User: william porter
class RollForLuckBot(Bot):

    def make_throw(self, scores, last_round):
        while sum(self.current_throws) < 21:
            yield True
        score_to_beat = max([x for i,x in enumerate(scores) if i!=self.index]) + 10
        score_to_beat = max(score_to_beat, 44)
        current_score = scores[self.index] + sum(self.current_throws)
        while (last_round or (current_score >= 40)):
            current_score = scores[self.index] + sum(self.current_throws)
            if current_score > score_to_beat:
                break
            yield True
        # roll more if we're feeling lucky    
        while (random.randint(1,6) == self.current_throws[-1]):
            yield True    
        yield False


# User: Martijn Vissers
class FlipCoinRollDice(Bot):
    def make_throw(self, scores, last_round):
        while random.randint(1,2) == 2:
            throws = random.randint(1,6) != 6
            x = 0
            while x < throws:
                x = x + 1
                yield True
        yield False


# User: Spitemaster
class GoHomeBot(Bot):
    def make_throw(self, scores, last_round):
        while scores[self.index] + sum(self.current_throws) < 40:
            yield True
        yield False


# User: Spitemaster
class LastRound(Bot):
    def make_throw(self, scores, last_round):
        while sum(self.current_throws) < 15 and not last_round and scores[self.index] + sum(self.current_throws) < 40:
            yield True
        while max(scores) > scores[self.index] + sum(self.current_throws):
            yield True
        yield False


# User: The_Bob
class PointsAreForNerdsBot(Bot):
    def make_throw(self, scores, last_round):
        while True:
            yield True


# User: The_Bob
class OneInFiveBot(Bot):
    def make_throw(self, scores, last_round):
        while random.randint(1,5) < 5:
            yield True
        yield False


# User: Cory Gehr
class MatchLeaderBot(Bot):
    # Try to match the current leader, then pass them in the last round
    def make_throw(self, scores, last_round):

        while True:
            current_top = max(scores)
            my_total = scores[self.index]
            my_round_total = sum(self.current_throws)
            my_current_total = my_total + my_round_total
            difference = current_top - my_current_total

            if last_round and my_current_total < current_top:
                # Go for gold while we still can
                yield True
                continue
            elif difference > 5:
                # Don't risk another throw if we could pass leader in one toss
                yield True
                continue
            break

        yield False


