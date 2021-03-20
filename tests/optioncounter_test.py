from optioncounter import OptionCounter

def test_should_init():
    counter = OptionCounter(1, 10, 1, 5)
    assert counter.value == 5

def test_should_init_without_start():
    counter = OptionCounter(1, 10, 1)
    assert counter.value == 1

def test_should_increment():
    counter = OptionCounter(1, 10, 1, 5)
    counter.next()
    assert counter.value == 6

def test_should_decrement():
    counter = OptionCounter(1, 10, 1, 5)
    counter.previous()
    assert counter.value == 4

def test_should_not_increment_beyond_max():
    counter = OptionCounter(1, 10, 2, 9)
    counter.next()
    assert counter.value == 10

def test_should_not_decrement_beyond_min():
    counter = OptionCounter(1, 10, 2, 2)
    counter.previous()
    assert counter.value == 1