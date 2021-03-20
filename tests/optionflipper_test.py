from birbcam.optionflipper import OptionFlipper

def test_should_init():
    flipper = OptionFlipper([1, 2, 3], 1, ["a", "b", "c"])
    assert flipper.value == 2
    assert flipper.label == "b"

def test_should_init_without_labels():
    flipper = OptionFlipper([1, 2, 3], 1)
    assert flipper.value == 2
    assert flipper.label == "2"

def test_should_flip_to_next():
    flipper = OptionFlipper(["a", "b", "c"])
    flipper.next()
    assert flipper.value == "b"

def test_should_flip_to_previous():
    flipper = OptionFlipper(["a", "b", "c"], 1)
    flipper.previous()
    assert flipper.value == "a"

def test_should_flip_back_to_start():
    flipper = OptionFlipper(["a", "b", "c"], 2)
    flipper.next()
    assert flipper.value == "a"

def test_should_flip_forward_to_end():
    flipper = OptionFlipper(["a", "b", "c"], 0)
    flipper.previous()
    assert flipper.value == "c"