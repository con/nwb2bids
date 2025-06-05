from clize import run
from nwb2bids import base

# def reposit():
#   run(base.reposit)


def main():
    run(
        {
            "reposit": base.reposit,
        }
    )


if __name__ == "__main__":
    main()
