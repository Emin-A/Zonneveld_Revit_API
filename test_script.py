import wpf
from System.Windows import Window


class TestWindow(Window):
    def __init__(self):
        wpf.LoadComponent(self, "TestUI.xaml")  # A basic .xaml file you can create


win = TestWindow()
win.ShowDialog()
