import re
from curses.ascii import isdigit
from nltk.corpus import cmudict

class cmusyllables(object):

    def __init__(self):

        self.dcSyllableDict = cmudict.dict()

        #-----
        # New structures for the SyllableCount3 routine

        self.dcSyllable3WordCache = {}

        self.liSyllable3SubSyllables = [
            'cial',
            'tia',
            'cius',
            'cious',
            'uiet',
            'gious',
            'geous',
            'priest',
            'giu',
            'dge',
            'ion',
            'iou',
            'sia$',
            '.che$',
            '.ched$',
            '.abe$',
            '.ace$',
            '.ade$',
            '.age$',
            '.aged$',
            '.ake$',
            '.ale$',
            '.aled$',
            '.ales$',
            '.ane$',
            '.ame$',
            '.ape$',
            '.are$',
            '.ase$',
            '.ashed$',
            '.asque$',
            '.ate$',
            '.ave$',
            '.azed$',
            '.awe$',
            '.aze$',
            '.aped$',
            '.athe$',
            '.athes$',
            '.ece$',
            '.ese$',
            '.esque$',
            '.esques$',
            '.eze$',
            '.gue$',
            '.ibe$',
            '.ice$',
            '.ide$',
            '.ife$',
            '.ike$',
            '.ile$',
            '.ime$',
            '.ine$',
            '.ipe$',
            '.iped$',
            '.ire$',
            '.ise$',
            '.ished$',
            '.ite$',
            '.ive$',
            '.ize$',
            '.obe$',
            '.ode$',
            '.oke$',
            '.ole$',
            '.ome$',
            '.one$',
            '.ope$',
            '.oque$',
            '.ore$',
            '.ose$',
            '.osque$',
            '.osques$',
            '.ote$',
            '.ove$',
            '.pped$',
            '.sse$',
            '.ssed$',
            '.ste$',
            '.ube$',
            '.uce$',
            '.ude$',
            '.uge$',
            '.uke$',
            '.ule$',
            '.ules$',
            '.uled$',
            '.ume$',
            '.une$',
            '.upe$',
            '.ure$',
            '.use$',
            '.ushed$',
            '.ute$',
            '.ved$',
            '.we$',
            '.wes$',
            '.wed$',
            '.yse$',
            '.yze$',
            '.rse$',
            '.red$',
            '.rce$',
            '.rde$',
            '.ily$',
            '.ely$',
            '.des$',
            '.gged$',
            '.kes$',
            '.ced$',
            '.ked$',
            '.med$',
            '.mes$',
            '.ned$',
            '.[sz]ed$',
            '.nce$',
            '.rles$',
            '.nes$',
            '.pes$',
            '.tes$',
            '.res$',
            '.ves$',
            'ere$'
        ]

        #global $split_array;
        self.liSyllable3AddSyllables  = [
            'ia',
            'riet',
            'dien',
            'ien',
            'iet',
            'iu',
            'iest',
            'io',
            'ii',
            'ily',
            '.oala$',
            '.iara$',
            '.ying$',
            '.earest',
            '.arer',
            '.aress',
            '.eate$',
            '.eation$',
            '[aeiouym]bl$',
            '[aeiou]{3}',
            '^mc','ism',
            '^mc','asm',
            '([^aeiouy])1l$',
            '[^l]lien',
            '^coa[dglx].',
            '[^gq]ua[^auieo]',
            'dnt$'
        ]

        #-----
        # Create a list of the compiled regex

        self.liSyllable3RESubSyllables = []
        self.liSyllable3REAddSyllables = []

        for LszRegEx in self.liSyllable3AddSyllables:
            LreRegEx = re.compile(LszRegEx)
            self.liSyllable3REAddSyllables.append(LreRegEx)

        for LszRegEx in self.liSyllable3SubSyllables:
            LreRegEx = re.compile(LszRegEx)
            self.liSyllable3RESubSyllables.append(LreRegEx)

    def NonCMUSyllableCount(self, AszWord):

        #LszWord = self._normalize_word( AszWord.lower() )
        LszWord = AszWord

        #-----
        # If we've already seen this before then return the syllables

        if LszWord in self.dcSyllable3WordCache:
            return(self.dcSyllable3WordCache[LszWord])

        #-----
        #Split into parts on vowels and vowel sounds

        LliWordParts = re.split(r'[^aeiouy]+', LszWord)

        #-----
        # Combine the valid parts of the word

        LliValidWordParts = []

        for LszValue in LliWordParts:
            if LszValue <> '':
                LliValidWordParts.append(LszValue)

        LinSyllables = 0

        #-----
        # Loop through the compiled regexs looking for matches

        for LreSylRE in self.liSyllable3RESubSyllables:
            LinMatch = 0 if LreSylRE.search(LszWord) is None else 1
            LinSyllables -= LinMatch

        for LreSylRE in self.liSyllable3REAddSyllables:
            LinMatch = 0 if LreSylRE.search(LszWord) is None else 1
            LinSyllables += LinMatch

        #-----
        # Now compute the syllable count by the number of vowels

        LinSyllables += len(LliValidWordParts)

        #-----
        # If we've not found any there must be at least 1

        LinSyllables = 1 if LinSyllables == 0 else LinSyllables

        #----
        # Record this result in the word cache

        self.dcSyllable3WordCache[LszWord] = LinSyllables

        #-----
        # Return the result

        return(LinSyllables)

    def SyllableCount(self, AszWord, AlgFallBack=True):
        LszWord = AszWord.lower()

        if len(LszWord) == 0 or LszWord not in self.dcSyllableDict:
            if len(LszWord) == 0 or not AlgFallBack:
                return(0)
            else:
                LliSyllableList = list((self.NonCMUSyllableCount(LszWord),))
        else:
            LliSyllableList = [len(list(y for y in x if isdigit(y[-1]))) for x in self.dcSyllableDict[LszWord]]

        return max(LliSyllableList)