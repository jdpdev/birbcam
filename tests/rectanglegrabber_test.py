from birbcam.rectanglegrabber import RectangleGrabber
from cv2 import EVENT_LBUTTONDOWN, EVENT_LBUTTONUP, EVENT_MOUSEMOVE

def test_tl_to_br_drag(mocker):
    mock_handler = None
    def mockSetClickHandler(window, handler):
        nonlocal mock_handler
        mock_handler = handler

    def mock_drag_done(bounds):
        assert bounds == ((300, 300), (400, 400))

    mocker.patch(
        'cv2.setMouseCallback',
        mockSetClickHandler
    )

    rect = RectangleGrabber("test", (800,600), onEnd=mock_drag_done)
    assert not rect.isDragging

    mock_handler(EVENT_LBUTTONDOWN, 300, 300, "", "")
    assert rect.isDragging
    assert rect.bounds == ((300, 300), (300, 300))

    mock_handler(EVENT_MOUSEMOVE, 400, 400, "", "")
    assert rect.bounds == ((300, 300), (400, 400))

    mock_handler(EVENT_LBUTTONUP, 500, 500, "", "")

def test_tl_to_br_drag_with_aspect_ratio(mocker):
    mock_handler = None
    def mockSetClickHandler(window, handler):
        nonlocal mock_handler
        mock_handler = handler

    def mock_drag_done(bounds):
        assert bounds == ((0, 0), (800, 800))

    mocker.patch(
        'cv2.setMouseCallback',
        mockSetClickHandler
    )

    rect = RectangleGrabber("test", (800,800), preserveAspectRatio=True, onEnd=mock_drag_done)
    assert not rect.isDragging

    mock_handler(EVENT_LBUTTONDOWN, 0, 0, "", "")
    assert rect.isDragging
    assert rect.bounds == ((0, 0), (0, 0))

    mock_handler(EVENT_MOUSEMOVE, 800, 600, "", "")
    assert rect.bounds == ((0, 0), (800, 800))

    mock_handler(EVENT_LBUTTONUP, 500, 500, "", "")
    
def test_tr_to_bl_drag(mocker):
    mock_handler = None
    def mockSetClickHandler(window, handler):
        nonlocal mock_handler
        mock_handler = handler

    def mock_drag_done(bounds):
        assert bounds == ((400, 200), (600, 400))

    mocker.patch(
        'cv2.setMouseCallback',
        mockSetClickHandler
    )

    rect = RectangleGrabber("test", (800,600), onEnd=mock_drag_done)
    assert not rect.isDragging

    mock_handler(EVENT_LBUTTONDOWN, 600, 200, "", "")
    assert rect.isDragging
    assert rect.bounds == ((600, 200), (600, 200))

    mock_handler(EVENT_MOUSEMOVE, 400, 400, "", "")
    assert rect.bounds == ((400, 200), (600, 400))

    mock_handler(EVENT_LBUTTONUP, 400, 400, "", "")
    
def test_tr_to_bl_drag_with_aspect_ratio(mocker):
    mock_handler = None
    def mockSetClickHandler(window, handler):
        nonlocal mock_handler
        mock_handler = handler

    def mock_drag_done(bounds):
        assert bounds == ((400, 0), (800, 400))

    mocker.patch(
        'cv2.setMouseCallback',
        mockSetClickHandler
    )

    rect = RectangleGrabber("test", (800,800), preserveAspectRatio=True, onEnd=mock_drag_done)
    assert not rect.isDragging

    mock_handler(EVENT_LBUTTONDOWN, 800, 0, "", "")
    assert rect.isDragging
    assert rect.bounds == ((800, 0), (800, 0))

    mock_handler(EVENT_MOUSEMOVE, 400, 200, "", "")
    assert rect.bounds == ((400, 0), (800, 400))

    mock_handler(EVENT_LBUTTONUP, 400, 400, "", "")
    
def test_br_to_tl_drag(mocker):
    mock_handler = None
    def mockSetClickHandler(window, handler):
        nonlocal mock_handler
        mock_handler = handler

    def mock_drag_done(bounds):
        assert bounds == ((400, 400), (600, 600))

    mocker.patch(
        'cv2.setMouseCallback',
        mockSetClickHandler
    )

    rect = RectangleGrabber("test", (800,600), onEnd=mock_drag_done)
    assert not rect.isDragging

    mock_handler(EVENT_LBUTTONDOWN, 600, 600, "", "")
    assert rect.isDragging
    assert rect.bounds == ((600, 600), (600, 600))

    mock_handler(EVENT_MOUSEMOVE, 400, 400, "", "")
    assert rect.bounds == ((400, 400), (600, 600))

    mock_handler(EVENT_LBUTTONUP, 400, 400, "", "")
    
def test_br_to_tl_drag_with_aspect_ratio(mocker):
    mock_handler = None
    def mockSetClickHandler(window, handler):
        nonlocal mock_handler
        mock_handler = handler

    def mock_drag_done(bounds):
        assert bounds == ((400, 400), (800, 800))

    mocker.patch(
        'cv2.setMouseCallback',
        mockSetClickHandler
    )

    rect = RectangleGrabber("test", (800,800), preserveAspectRatio=True, onEnd=mock_drag_done)
    assert not rect.isDragging

    mock_handler(EVENT_LBUTTONDOWN, 800, 800, "", "")
    assert rect.isDragging
    assert rect.bounds == ((800, 800), (800, 800))

    mock_handler(EVENT_MOUSEMOVE, 400, 200, "", "")
    assert rect.bounds == ((400, 400), (800, 800))

    mock_handler(EVENT_LBUTTONUP, 400, 400, "", "")
    
def test_bl_to_tr_drag(mocker):
    mock_handler = None
    def mockSetClickHandler(window, handler):
        nonlocal mock_handler
        mock_handler = handler

    def mock_drag_done(bounds):
        assert bounds == ((200, 400), (400, 600))

    mocker.patch(
        'cv2.setMouseCallback',
        mockSetClickHandler
    )

    rect = RectangleGrabber("test", (800,600), onEnd=mock_drag_done)
    assert not rect.isDragging

    mock_handler(EVENT_LBUTTONDOWN, 200, 600, "", "")
    assert rect.isDragging
    assert rect.bounds == ((200, 600), (200, 600))

    mock_handler(EVENT_MOUSEMOVE, 400, 400, "", "")
    assert rect.bounds == ((200, 400), (400, 600))

    mock_handler(EVENT_LBUTTONUP, 400, 400, "", "")
    
def test_bl_to_tr_drag_with_aspect_ratio(mocker):
    mock_handler = None
    def mockSetClickHandler(window, handler):
        nonlocal mock_handler
        mock_handler = handler

    def mock_drag_done(bounds):
        assert bounds == ((0, 400), (400, 800))

    mocker.patch(
        'cv2.setMouseCallback',
        mockSetClickHandler
    )

    rect = RectangleGrabber("test", (800,800), preserveAspectRatio=True, onEnd=mock_drag_done)
    assert not rect.isDragging

    mock_handler(EVENT_LBUTTONDOWN, 0, 800, "", "")
    assert rect.isDragging
    assert rect.bounds == ((0, 800), (0, 800))

    mock_handler(EVENT_MOUSEMOVE, 400, 200, "", "")
    assert rect.bounds == ((0, 400), (400, 800))

    mock_handler(EVENT_LBUTTONUP, 400, 400, "", "")