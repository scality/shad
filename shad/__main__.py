"""``python -m shad [root]`` - print a summary of the local SHAD copy."""

import sys

from . import SHAD


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ds = SHAD(argv[0] if argv else None)
    print(ds)
    print()
    print(ds.summary().to_string(index=False))
    train, test = ds.split()
    print(f"\nPaper split: {len(train)} nominal series for training, {len(test)} anomalous for testing.")


if __name__ == "__main__":
    main()
