import unittest 

from unittest.mock import patch, MagicMock, Mock
from birbcam.exposureadjust.sleep import Sleep

@patch('time.time', MagicMock(return_value=100))
def test_time_to_update():
    def mockChangeState(state):
        assert state == None

    sleep = Sleep(50)
    sleep.take_over(None, None, None, mockChangeState, 100, 10)
    sleep.update(None, None)

@patch('time.time', MagicMock(return_value=25))
def test_not_time_to_update():
    mockChangeState = Mock()
    sleep = Sleep(50)
    sleep.take_over(None, None, None, mockChangeState, 100, 10)
    sleep.update(None, None)

    assert not mockChangeState.called
