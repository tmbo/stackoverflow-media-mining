import re
from curses.ascii import isdigit
from nltk.corpus import cmudict


class CMUSyllables(object):
    def __init__(self):

        self.dc_syllable_dict = cmudict.dict()

        # New structures for the SyllableCount3 routine

        self.dc_syllable3_word_cache = {}

        self.li_syllable3_sub_syllables = [
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

        # global $split_array;
        self.li_syllable3_add_syllables = [
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
            '^mc', 'ism',
            '^mc', 'asm',
            '([^aeiouy])1l$',
            '[^l]lien',
            '^coa[dglx].',
            '[^gq]ua[^auieo]',
            'dnt$'
        ]

        # Create a list of the compiled regex

        self.li_syllable3_re_sub_syllables = []
        self.li_syllable3_re_add_syllables = []

        for lsz_regex in self.li_syllable3_add_syllables:
            lre_regex = re.compile(lsz_regex)
            self.li_syllable3_re_add_syllables.append(lre_regex)

        for lsz_regex in self.li_syllable3_sub_syllables:
            lre_regex = re.compile(lsz_regex)
            self.li_syllable3_re_sub_syllables.append(lre_regex)

    def non_cmu_syllable_count(self, asz_word):

        # LszWord = self._normalize_word( AszWord.lower() )
        lsz_word = asz_word

        # If we've already seen this before then return the syllables

        if lsz_word in self.dc_syllable3_word_cache:
            return self.dc_syllable3_word_cache[lsz_word]

        # Split into parts on vowels and vowel sounds

        lli_word_parts = re.split(r'[^aeiouy]+', lsz_word)

        # Combine the valid parts of the word

        lli_valid_word_parts = []

        for lsz_value in lli_word_parts:
            if lsz_value != '':
                lli_valid_word_parts.append(lsz_value)

        lin_syllables = 0

        # Loop through the compiled regexs looking for matches

        for LreSylRE in self.li_syllable3_re_sub_syllables:
            lin_match = 0 if LreSylRE.search(lsz_word) is None else 1
            lin_syllables -= lin_match

        for LreSylRE in self.li_syllable3_re_add_syllables:
            lin_match = 0 if LreSylRE.search(lsz_word) is None else 1
            lin_syllables += lin_match

        # Now compute the syllable count by the number of vowels

        lin_syllables += len(lli_valid_word_parts)

        # If we've not found any there must be at least 1

        lin_syllables = 1 if lin_syllables == 0 else lin_syllables

        # Record this result in the word cache

        self.dc_syllable3_word_cache[lsz_word] = lin_syllables

        # Return the result

        return lin_syllables

    def syllable_count(self, asz_word, alg_fallback=True):
        lsz_word = asz_word.lower()

        if len(lsz_word) == 0 or lsz_word not in self.dc_syllable_dict:
            if len(lsz_word) == 0 or not alg_fallback:
                return 0
            else:
                lli_syllable_list = list((self.non_cmu_syllable_count(lsz_word),))
        else:
            lli_syllable_list = [len(list(y for y in x if isdigit(y[-1]))) for x in self.dc_syllable_dict[lsz_word]]

        return max(lli_syllable_list)