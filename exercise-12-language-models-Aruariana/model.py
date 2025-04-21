from typing import Iterator

import torch
from torch import nn

from tokenizer import Tokenizer


class NextTokenModel(nn.Module):
    """

    Simple model that predicts a distribution over the next token
    given a sequence of tokens of fixed length, called context, as input.

    """

    def __init__(
        self,
        vocab_size: int,
        context_length: int,
        hidden_dim: int,
    ) -> None:
        super().__init__()
        self.vocab_size = vocab_size
        self.context_length = context_length

        # TODO: setup model parameters and layers
        raise NotImplementedError

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        assert token_ids.shape[1] == self.context_length, \
            f"only support context length of {self.context_length}"

        # TODO: implement forward pass
        raise NotImplementedError


def sample_next_token(
    probs: torch.Tensor,
    k: int
) -> int:
    """

    Samples the next token id based on the given probability distribution.
    Normalizes the top k most probable next token ids and randomly samples
    from that distribution.
    Note that k=1 is equivalent to greedy decoding, namely
    taking the token id with the highest probability.

    >>> import torch
    >>> probs = torch.tensor([0.8, 0.2])
    >>> sample_next_token(probs, 1)
    0
    >>> probs = torch.tensor([0.1, 0.5, 0.4])
    >>> sample_next_token(probs, 1)
    1

    The following doctests might fail sometimes, because they are
    sampling based.
    >>> probs = torch.tensor([0.1, 0.32, 0.48, 0.1])
    >>> samples = [sample_next_token(probs, 2) for _ in range(1000)]
    >>> round(sum(s == 1 for s in samples) / 1000, 1)
    0.4
    >>> round(sum(s == 2 for s in samples) / 1000, 1)
    0.6
    >>> probs = torch.tensor([0.3, 0.2, 0.4, 0.1])
    >>> samples = [sample_next_token(probs, 4) for _ in range(1000)]
    >>> round(sum(s == 0 for s in samples) / 1000, 1)
    0.3
    >>> round(sum(s == 1 for s in samples) / 1000, 1)
    0.2
    >>> round(sum(s == 2 for s in samples) / 1000, 1)
    0.4
    >>> round(sum(s == 3 for s in samples) / 1000, 1)
    0.1
    """
    assert abs(1.0 - probs.sum().item()) <= 1e-5, \
        "probs must sum to 1.0"
    assert 0 < k <= len(probs), \
        f"k must be between 1 and {len(probs):,}"

    # TODO: implement sampling from the top k most likely tokens
    raise NotImplementedError


@torch.inference_mode()
def inference(
    prefix: str,
    model: NextTokenModel,
    tokenizer: Tokenizer,
    max_new_tokens: int,
    k: int,
    device: torch.device,
) -> Iterator[str]:
    """

    Generates text starting from the given prefix using the given model
    token by token until the maximum number of new tokens is reached.
    Next token is determined by sampling from the top k most likely tokens
    the model predicts.

    """
    # inital token ids
    token_ids = tokenizer.tokenize(prefix)

    model = model.to(device)

    num_initial_tokens = len(token_ids)
    while len(token_ids) - num_initial_tokens < max_new_tokens:
        # prepare input token ids
        input_token_ids = tokenizer.pad(token_ids, model.context_length)
        input_token_ids = input_token_ids[-model.context_length:]

        # create input tensor with single batch dimension
        input_tensor = torch.tensor(
            input_token_ids,
            device=device
        ).unsqueeze(0)

        # run model
        logits = model(input_tensor)[0]
        probs = torch.softmax(logits, dim=0)

        # get next token id and append to token ids
        next_token_id = sample_next_token(probs, k)
        token_ids.append(int(next_token_id))

        # yield the current text
        yield tokenizer.de_tokenize(token_ids)
 