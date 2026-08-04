from krita import Krita
from .infinite_canvas import InfiniteCanvasExtension

instance = Krita.instance()
extension = InfiniteCanvasExtension(parent=instance)
instance.addExtension(extension)
