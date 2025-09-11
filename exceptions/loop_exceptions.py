class LoopBreakException(Exception):
    """Exception để thoát ngay lập tức khỏi vòng lặp For"""
    pass

class LoopSkipException(Exception):
    """Exception để skip iteration hiện tại"""
    pass
