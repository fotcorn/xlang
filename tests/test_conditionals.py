from .conftest import run


# if/else
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
            } else {
                i = 2;
            }
            assert(i == 2);
        }
    """
    )


# basic elif
def test_elif_not_executed():
    run(
        """
        main() {
            i: int = 0;
            if (false) {
                i = 1;
                assert(false);
            } elif (false) {
                i = 2;
                assert(false);
            }
            assert(i == 0);
        }
        """
    )


def test_elif_if_executed():
    run(
        """
        main() {
            i: int = 0;
            if (true) {
                i = 1;
            } elif (false) {
                i = 2;
                assert(false);
            }
            assert(i == 1);
        }
        """
    )


def test_elif_if_executed2():
    run(
        """
        main() {
            i: int = 0;
            if (true) {
                i = 1;
            } elif (true) {
                i = 2;
                assert(false);
            }
            assert(i == 1);
        }
        """
    )


def test_elif_elif_executed():
    run(
        """
        main() {
            i: int = 0;
            if (false) {
                i = 1;
                assert(false);
            } elif (true) {
                i = 2;
            }
            assert(i == 2);
        }
        """
    )


def test_elif_elif2_executed():
    run(
        """
        main() {
            i: int = 0;
            if (false) {
                i = 1;
                assert(false);
            } elif (true) {
                i = 2;
            }
            elif (false) {
                i = 3;
                assert(false);
            }
            assert(i == 2);
        }
        """
    )


# elif + else
def test_elifelse():
    run(
        """
        main() {
            i: int = 0;
            if (false) {
                i = 1;
                assert(false);
            } elif (false) {
                i = 2;
                assert(false);
            } else {
                i = 3;
            }
            assert(i == 3);
        }
        """
    )


def test_elifelse2():
    run(
        """
        main() {
            i: int = 0;
            if (false) {
                i = 1;
                assert(false);
            } elif (true) {
                i = 2;
            } else {
                i = 3;
                assert(false);
            }
            assert(i == 2);
        }
        """
    )


def test_elifelse3():
    run(
        """
        main() {
            i: int = 0;
            if (true) {
                i = 1;
            } elif (true) {
                i = 2;
                assert(false);
            } else {
                i = 3;
                assert(false);
            }
            assert(i == 1);
        }
        """
    )
