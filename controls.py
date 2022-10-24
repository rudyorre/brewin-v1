class Control_WHILE:
    def __init__(self):
        self.ENDWHILE_line = None

class Control_ENDWHILE:
    def __init__(self):
        self.WHILE_line = None

class Control_IF:
    def __init__(self) -> None:
        self.ELSE_line = None
        self.ENDIF_line = None

class Control_ELSE:
    def __init__(self):
        self.ENDIF_line = None