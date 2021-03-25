import unittest 
import time

from unittest.mock import patch, MagicMock, Mock
from birbcam.exposureadjust.adjustdown import AdjustDown

class TestFlipper():
    __test__ = False

    def __init__(self, isAtStart, step):
        self._isAtStart = isAtStart
        self._step = step

    @property
    def is_at_start(self):
        return self._isAtStart

    def previous(self):
        return self._step

class TestCamera():
    __test__ = False

    def __init__(self, expectShutter):
        self._expectShutter = expectShutter

    @property
    def shutter_speed(self):
        return 10000

    @shutter_speed.setter
    def shutter_speed(self, value):
        assert self._expectShutter == value
        

def test_do_adjust_changes_shutter():
    mockChangeState = Mock()

    adjustdown = AdjustDown()
    adjustdown.take_over(
        None,
        TestFlipper(False, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    adjustdown.do_adjust(TestCamera(10000))

def test_do_adjust_finish():
    mockChangeState = Mock()

    adjustdown = AdjustDown()
    adjustdown.finish = Mock()
    adjustdown.take_over(
        None,
        TestFlipper(True, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    adjustdown.do_adjust(TestCamera(10000))
    assert adjustdown.finish.called

def test_check_exposure_not_finished():
    mockChangeState = Mock()

    adjustdown = AdjustDown()
    adjustdown.finish = Mock()
    adjustdown.take_over(
        None,
        TestFlipper(True, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    assert not adjustdown.check_exposure(50)

def test_check_exposure_within_margin():
    mockChangeState = Mock()

    adjustdown = AdjustDown()
    adjustdown.finish = Mock()
    adjustdown.take_over(
        None,
        TestFlipper(True, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    assert adjustdown.check_exposure(109)
    adjustdown.reset_last_exposure()
    assert adjustdown.check_exposure(91)

def test_check_exposure_not_crossed_target():
    mockChangeState = Mock()

    adjustdown = AdjustDown()
    adjustdown.finish = Mock()
    adjustdown.take_over(
        None,
        TestFlipper(True, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    adjustdown.check_exposure(50)
    assert not adjustdown.check_exposure(75)

@patch('time.time', side_effect=[0, 30])
@patch('birbcam.exposureadjust.adjust.calculate_exposure', side_effect=[50, 125])
def test_check_exposure_crossed_target(mock_time, mock_calculate_exposure):
    mockChangeState = Mock()

    adjustdown = AdjustDown()
    adjustdown.finish = Mock()
    adjustdown.take_over(
        None,
        TestFlipper(False, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    assert not adjustdown.check_exposure(50)
    adjustdown._lastExposure = 50
    assert adjustdown.check_exposure(125)