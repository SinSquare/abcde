"""Text parsing utils"""

import re
import math
from collections import Counter
from abc import ABC, abstractmethod
from dateutil import parser


class Tag(ABC):
    """Tag"""

    def __init__(self, tag):
        self.tag = tag

    def tag_name(self):
        return self.tag

    @abstractmethod
    def matches(self, word):
        pass


class SimilarityMatcher:
    """SimilarityMatcher"""

    def __init__(self, words, similarity=0.9, exact_match=False):
        self.words = words
        self.similarity = similarity
        self.exact_match = exact_match

    def word_match(self, word):
        for w in self.words:
            sim = self.get_cosine_sim(w, word)
            if sim >= self.similarity:
                return word
        return False

    def get_cosine_sim(self, str1, str2):
        # Vectorize the strings based on character frequency
        vec1 = Counter(str1.lower())
        vec2 = Counter(str2.lower())

        # Dot Product
        intersection = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[x] * vec2[x] for x in intersection)

        # Magnitude
        mag1 = math.sqrt(sum(val**2 for val in vec1.values()))
        mag2 = math.sqrt(sum(val**2 for val in vec2.values()))

        return dot_product / (mag1 * mag2) if (mag1 * mag2) else 0


class SimilarityTag(Tag):
    """SimilarityTag"""

    def __init__(self, tag, words, similarity=0.9, exact_match=False):
        self.matcher = SimilarityMatcher(words, similarity, exact_match)
        super().__init__(tag)

    def matches(self, word):
        return self.matcher.word_match(word)


class ReTag(Tag):
    """ReTag"""

    def __init__(self, tag, exp):
        self.exp = re.compile(exp)
        super().__init__(tag)

    def matches(self, word):
        if self.exp.fullmatch(word):
            return word
        return False


class DateTag(Tag):
    """DateTag"""

    def matches(self, word):
        dt = parser.parse(word)
        if dt:
            return dt
        return False


class CompoundTag(Tag):
    """CompoundTag"""

    def __init__(self, tag, parts):
        self.parts = parts
        self.matched_tag = None
        super().__init__(tag)

    def matches(self, word):
        for part in self.parts:
            if part.matches(word):
                self.matched_tag = part
                return word
        return False

    def tag_name(self):
        return self.matched_tag.tag
