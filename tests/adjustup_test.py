import unittest 
import time

from unittest.mock import patch, MagicMock, Mock
from birbcam.exposureadjust.adjustup import AdjustUp

class TestFlipper():
    __test__ = False

    def __init__(self, isAtEnd, step):
        self._isAtEnd = isAtEnd
        self._step = step

    @property
    def is_at_end(self):
        return self._isAtEnd

    def next(self):
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

    adjustup = AdjustUp()
    adjustup.take_over(
        None,
        TestFlipper(False, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    adjustup.do_adjust(TestCamera(10000))

def test_do_adjust_finish():
    mockChangeState = Mock()

    adjustup = AdjustUp()
    adjustup.finish = Mock()
    adjustup.take_over(
        None,
        TestFlipper(True, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    adjustup.do_adjust(TestCamera(10000))
    assert adjustup.finish.called

def test_check_exposure_not_finished():
    mockChangeState = Mock()

    adjustup = AdjustUp()
    adjustup.finish = Mock()
    adjustup.take_over(
        None,
        TestFlipper(True, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    assert not adjustup.check_exposure(50)

def test_check_exposure_within_margin():
    mockChangeState = Mock()

    adjustup = AdjustUp()
    adjustup.finish = Mock()
    adjustup.take_over(
        None,
        TestFlipper(True, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    assert adjustup.check_exposure(109)
    adjustup.reset_last_exposure()
    assert adjustup.check_exposure(91)

def test_check_exposure_not_crossed_target():
    mockChangeState = Mock()

    adjustup = AdjustUp()
    adjustup.finish = Mock()
    adjustup.take_over(
        None,
        TestFlipper(True, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    adjustup.check_exposure(50)
    assert not adjustup.check_exposure(75)

@patch('time.time', side_effect=[0, 30])
@patch('birbcam.exposureadjust.adjust.calculate_exposure', side_effect=[50, 125])
def test_check_exposure_crossed_target(mock_time, mock_calculate_exposure):
    mockChangeState = Mock()

    adjustup = AdjustUp()
    adjustup.finish = Mock()
    adjustup.take_over(
        None,
        TestFlipper(False, 10000),
        TestFlipper(False, 100),
        mockChangeState,
        100,
        10
    )

    assert not adjustup.check_exposure(50)
    adjustup._lastExposure = 50
    assert adjustup.check_exposure(125)