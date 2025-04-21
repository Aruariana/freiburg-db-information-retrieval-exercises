import argparse
import random

import torch
from torch import optim

from model import (
    NextTokenModel,
    inference
)
from tokenizer import (
    Tokenizer,
    CharacterTokenizer,
    WordTokenizer,
)


def train(args: argparse.Namespace) -> None:
    # set options to make training reproducible
    torch.manual_seed(2324)

    device = torch.device(args.device)

    # load data
    texts = []
    for file in sorted(args.files):
        with open(file, "r", encoding="utf8") as inf:
            text = inf.read().strip()
            texts.append(text)

    # create tokenizer and model
    tokenizer: Tokenizer  # to make mypy happy
    if args.tokenizer == "character":
        tokenizer = CharacterTokenizer()
        # use 64 as default context length for character-level models
        args.context_length = args.context_length or 64
    else:
        tokenizer = WordTokenizer()
        tokenizer.build(texts, args.min_word_frequency)
        # use 16 as default context length for word-level models
        args.context_length = args.context_length or 16

    print(
        f"Using {args.tokenizer} tokenizer with "
        f"vocab size of {tokenizer.vocab_size():,}"
    )

    model = NextTokenModel(
        tokenizer.vocab_size(),
        args.context_length,
        args.hidden_dim
    ).to(device)
    num_params = sum(p.numel() for p in model.parameters())
    print(f"Model has {num_params:,} parameters")

    # prepare training data
    step = max(1, args.context_length // 4)
    samples = []
    for text in texts:
        token_ids = tokenizer.tokenize(text)

        for i in range(0, len(token_ids), step):
            sample = token_ids[max(0, i - args.context_length):i]
            sample = tokenizer.pad(sample, args.context_length)
            label = token_ids[i]

            samples.append((sample, label))

    # shuffle before split
    random.seed(2324)
    random.shuffle(samples)

    # split train and validation
    train_samples = samples[args.num_val_samples:]
    val_samples = samples[:args.num_val_samples]
    print(f"Training on {len(train_samples):,} samples")
    print(f"Validating on {len(val_samples):,} samples")

    # we use Adam here instead of SGD
    # because this optimizer usually leads
    # to faster convergence
    optimizer = optim.Adam(  # noqa
        model.parameters(),
        args.learning_rate
    )

    # run training
    for epoch in range(args.num_epochs):
        # TODO: implement one epoch of training:
        # loop over the training samples in batches
        # and update model parameters after each batch
        # with the given optimizer
        raise NotImplementedError

        # save model after each epoch, so progress is not lost
        # if we stop training prematurely;
        # also save the hyperparameters
        # and tokenizer to be able to restore everything later
        # only from the checkpoint
        torch.save(
            {
                "tokenizer": args.tokenizer,
                "tokenizer_state": tokenizer.serialize(),
                "model_state": model.state_dict(),
                "hidden_dim": args.hidden_dim,
                "context_length": args.context_length,
            },
            args.checkpoint
        )
        if len(val_samples) == 0:
            continue

        # validate after each epoch by running inference
        # on some samples
        print("-" * 20)
        for sample, _ in val_samples:
            text = tokenizer.de_tokenize(sample)
            output = list(inference(
                text,
                model,
                tokenizer,
                args.context_length * 2,
                5,
                device
            ))[-1][len(text):]
            print(f"\n{text}\033[1m{output}\033[0m\n")
            print("-" * 20)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "files",
        type=str,
        nargs="+",
        help="text files to train on"
    )
    parser.add_argument(
        "-mwf",
        "--min-word-frequency",
        type=int,
        default=1,
        help="minimum word frequency for word tokenizer"
    )
    parser.add_argument(
        "-t",
        "--tokenizer",
        type=str,
        choices=["word", "character"],
        default="character",
        help="tokenizer to use"
    )
    parser.add_argument(
        "-e",
        "--num-epochs",
        type=int,
        default=10,
        help="number of epochs to train"
    )
    parser.add_argument(
        "-cl",
        "--context-length",
        type=int,
        default=None,
        help="number of tokens to use as context, default is 64 for character "
        "tokenizer and 16 for word tokenizer"
    )
    parser.add_argument(
        "-hd",
        "--hidden-dim",
        type=int,
        default=64,
        help="hidden dimensionality of the model"
    )
    parser.add_argument(
        "-lr",
        "--learning-rate",
        type=float,
        default=1e-3,
        help="learning rate for optimizer"
    )
    parser.add_argument(
        "-b",
        "--batch-size",
        type=int,
        default=32,
        help="batch size for training"
    )
    parser.add_argument(
        "-val",
        "--num-val-samples",
        type=int,
        default=4,
        help="number of samples to use for validation"
    )
    parser.add_argument(
        "-c",
        "--checkpoint",
        type=str,
        default="checkpoint.pt",
        help="path to checkpoint"
    )
    parser.add_argument(
        "-d",
        "--device",
        type=str,
        default="cpu",
        help="device to use for training"
    )
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())