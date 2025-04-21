import argparse
import time
import readline  # noqa

import torch

from model import (
    NextTokenModel,
    inference
)
from tokenizer import (
    CharacterTokenizer,
    WordTokenizer,
)


def test(args: argparse.Namespace) -> None:
    checkpoint = torch.load(args.checkpoint)

    device = torch.device(args.device)

    tokenizer_cls: type[
        CharacterTokenizer | WordTokenizer
    ]  # to make mypy happy
    if checkpoint["tokenizer"] == "character":
        tokenizer_cls = CharacterTokenizer
    else:
        tokenizer_cls = WordTokenizer

    tokenizer = tokenizer_cls.deserialize(checkpoint["tokenizer_state"])

    model = NextTokenModel(
        tokenizer.vocab_size(),
        checkpoint["context_length"],
        checkpoint["hidden_dim"]
    ).eval()
    model.load_state_dict(checkpoint["model_state"])

    while True:
        ipt = input(">> ")
        print()
        for output in inference(
            ipt,
            model,
            tokenizer,
            args.max_new_tokens,
            args.sample_top_k,
            device
        ):
            print(output)
            print()
            ipt = output
            if args.stop_at is not None and output.endswith(args.stop_at):
                break
            if args.sleep is not None:
                time.sleep(args.sleep / 1000.0)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--checkpoint",
        type=str,
        required=True,
        help="path to checkpoint"
    )
    parser.add_argument(
        "-t",
        "--max-new-tokens",
        type=int,
        default=128,
        help="maximum number of new tokens to generate"
    )
    parser.add_argument(
        "-stop",
        "--stop-at",
        type=str,
        default=None,
        help="stop generating when this string is generated"
    )
    parser.add_argument(
        "-topk",
        "--sample-top-k",
        type=int,
        default=5,
        help="sample from top k tokens"
    )
    parser.add_argument(
        "-d",
        "--device",
        type=str,
        default="cpu",
        help="device to run inference on"
    )
    parser.add_argument(
        "-s",
        "--sleep",
        type=int,
        default=None,
        help="sleep this many ms between generating tokens"
    )
    return parser.parse_args()


if __name__ == "__main__":
    test(parse_args())