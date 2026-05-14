#!/usr/bin/env python3
import sys

from wrapper_utils import run_bazel_target


def main():
    run_bazel_target("//:gazelle", extra_args=sys.argv[1:])


if __name__ == "__main__":
    main()
