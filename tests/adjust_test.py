import unittest 
import time

from unittest.mock import patch, MagicMock, Mock
from birbcam.exposureadjust.adjust import Adjust

class TestExposureAdjust():
    @property
    def sleepInterval(self):
        return 100

@patch('time.time', MagicMock(return_value=-25))
def test_not_time_to_update():
    with patch('birbcam.exposureadjust.utils.calculate_exposure', MagicMock(return_value=100)) as mock_calculate_exposure:
        mockChangeState = Mock()
        adjust = Adjust()
        adjust.take_over(None, None, None,  mockChangeState, 100, 10)
        adjust.update(None, None)

        assert not mock_calculate_exposure.called

@patch('time.time', MagicMock(return_value=0))
def test_finish_exposure_adjustment():
    with patch('birbcam.exposureadjust.adjust.calculate_exposure', MagicMock(return_value=100)) as mock_calculate_exposure:
        mockChangeState = Mock()

        adjust = Adjust()
        adjust.check_exposure = MagicMock(return_value=True)
        adjust.finish = Mock()
        
        adjust.take_over(TestExposureAdjust(), None, None, mockChangeState, 100, 10)
        adjust.update(None, None)

        assert adjust.finish.called


@patch('time.time', MagicMock(return_value=0))
def test_do_adjust():
    with patch('birbcam.exposureadjust.adjust.calculate_exposure', MagicMock(return_value=100)) as mock_calculate_exposure:
        mockChangeState = Mock()
        
        adjust = Adjust()
        adjust.check_exposure = MagicMock(return_value=False)
        adjust.do_adjust = Mock()

        adjust.take_over(TestExposureAdjust(), None, None, mockChangeState, 100, 10)
        adjust.update(None, None)

        assert adjust.do_adjust.called