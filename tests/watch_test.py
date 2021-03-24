import unittest 

from unittest.mock import patch, MagicMock, Mock
from birbcam.exposureadjust.watch import Watch
from birbcam.exposureadjust.adjustup import AdjustUp
from birbcam.exposureadjust.adjustdown import AdjustDown

@patch('time.time', MagicMock(return_value=25))
def test_not_time_to_update():
    with patch('birbcam.exposureadjust.utils.calculate_exposure', MagicMock(return_value=100)) as mock_calculate_exposure:
        mockChangeState = Mock()
        watch = Watch(50)
        watch.take_over(None, None, mockChangeState, 100, 10)
        watch.update(None, None)

        assert not mock_calculate_exposure.called

@patch('time.time', MagicMock(return_value=25))
@patch('birbcam.exposureadjust.utils.calculate_exposure', MagicMock(return_value=100))
def test_no_exposure_adjustment():
    mockChangeState = Mock()
    watch = Watch(50)
    watch.take_over(None, None, mockChangeState, 100, 10)
    watch.update(None, None)

    assert not mockChangeState.called

@patch('time.time', MagicMock(return_value=25))
@patch('birbcam.exposureadjust.utils.calculate_exposure', MagicMock(return_value=80))
def test_step_up():
    def mockChangeState(state):
        assert state.__class__.__name__ == AdjustUp.__class__.__name__
    
    watch = Watch(50)
    watch.take_over(None, None, mockChangeState, 100, 10)
    watch.update(None, None)

@patch('time.time', MagicMock(return_value=25))
@patch('birbcam.exposureadjust.utils.calculate_exposure', MagicMock(return_value=120))
def test_step_down():
    def mockChangeState(state):
        assert state.__class__.__name__ == AdjustDown.__class__.__name__
    
    watch = Watch(50)
    watch.take_over(None, None, mockChangeState, 100, 10)
    watch.update(None, None)