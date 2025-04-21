import string
import re
import json


class Tokenizer:
    pad_token_id: int
    unk_token_id: int

    def serialize(self) -> str:
        raise NotImplementedError

    @staticmethod
    def deserialize(s: str) -> "Tokenizer":
        raise NotImplementedError

    def vocab_size(self) -> int:
        raise NotImplementedError

    def pad(self, token_ids: list[int], length: int) -> list[int]:
        raise NotImplementedError

    def tokenize(self, s: str) -> list[int]:
        raise NotImplementedError

    def de_tokenize(self, token_ids: list[int]) -> str:
        raise NotImplementedError


class CharacterTokenizer(Tokenizer):
    def __init__(self) -> None:
        # unk token to represent unknowns
        self.unk_token_id = 0
        #  pad token to represent padding
        self.pad_token_id = 1
        self.vocab = {
            "<unk>": self.unk_token_id,
            "<pad>": self.pad_token_id
        }
        for c in (
            string.ascii_letters
            + string.digits
            + string.punctuation
            + string.whitespace
        ):
            self.vocab[c] = len(self.vocab)

        self.reverse_vocab = {
            i: c for c, i in self.vocab.items()
        }

    def serialize(self) -> str:
        return ""

    @staticmethod
    def deserialize(_: str) -> "CharacterTokenizer":
        return CharacterTokenizer()

    def pad(self, token_ids: list[int], length: int) -> list[int]:
        return [self.pad_token_id] * (length - len(token_ids)) + token_ids

    def vocab_size(self) -> int:
        return len(self.vocab)

    def tokenize(self, s: str) -> list[int]:
        return [
            self.vocab.get(c, self.unk_token_id)
            for c in s
        ]

    def de_tokenize(self, token_ids: list[int]) -> str:
        return "".join(
            self.reverse_vocab[token_id]
            for token_id in token_ids
            if token_id != self.pad_token_id  # dont output padding
        )


class WordTokenizer(Tokenizer):
    def __init__(self) -> None:
        self.unk_token_id = 0
        self.pad_token_id = 1
        self.vocab = {
            "<unk>": self.unk_token_id,
            "<pad>": self.pad_token_id
        }
        self.reverse_vocab = {
            self.unk_token_id: "<unk>",
            self.pad_token_id: "<pad>"
        }
        word = r"\b\w+(['-]\w+)*\b"
        self.word_pattern = re.compile(word)
        self.full_pattern = re.compile(rf"{word}|.", flags=re.DOTALL)

    def serialize(self) -> str:
        return json.dumps(self.vocab)

    @staticmethod
    def deserialize(s: str) -> "WordTokenizer":
        tokenizer = WordTokenizer()
        tokenizer.vocab = json.loads(s)
        tokenizer.reverse_vocab = {
            token_id: word
            for word, token_id in tokenizer.vocab.items()
        }
        return tokenizer

    def build(self, texts: list[str], min_freq: int) -> None:
        counts: dict[str, int] = {}
        for text in texts:
            for word in self.full_pattern.finditer(text):
                w = word.group().lower()
                counts[w] = counts.get(w, 0) + 1

        for w, freq in sorted(
            counts.items(),
            key=lambda x: x[1], reverse=True
        ):
            if freq < min_freq or w in self.vocab:
                continue
            self.vocab[w] = len(self.vocab)

        self.reverse_vocab = {
            token_id: word
            for word, token_id in self.vocab.items()
        }

    def pad(self, token_ids: list[int], length: int) -> list[int]:
        return [self.pad_token_id] * (length - len(token_ids)) + token_ids

    def vocab_size(self) -> int:
        return len(self.vocab)

    def tokenize(self, s: str) -> list[int]:
        return [
            self.vocab.get(word.group().lower(), self.unk_token_id)
            for word in self.full_pattern.finditer(s)
        ]

    def de_tokenize(self, token_ids: list[int]) -> str:
        return "".join(
            self.reverse_vocab[token_id]
            for token_id in token_ids
            if token_id != self.pad_token_id  # dont output padding
        )