from .conftest import run


def test_if():
    run(
        """
        main() {
            if (true) {
                assert(true);
            }
            if (false) {
                assert(false);
            }
        }
    """
    )


def test_if_else1():
    run(
        """
        main() {
            i: int = 0;
            if (true) {
                i = 1;
            } else {
                i = 2;
                assert(false);
            }
            assert(i == 1);
        }
    """
    )


def test_if_else2():
    run(
        """
        main() {
            i: int = 0;
            if (false) {
                i = 1;
                assert(false);
            }
            else {
                i = 2;
            }
            assert(i == 2);
        }
    """
    )
