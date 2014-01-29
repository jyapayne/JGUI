
class StructureBase(object):
    @classmethod
    def _attrs(cls):
        a = []
        i = cls()
        for attr in dir(i):
            if not attr.startswith('_') and not callable(getattr(i, attr)):
                a.append(attr)
        return a

    def _dict(self):
        d = {}
        attrs = self._attrs()
        for a in attrs:
            d[a] = getattr(self, a)
        return d

    def _dict_string(self):
        return ', '.join('{}={}'.format(key, val) for key, val in self._dict().items())

    def __repr__(self):
        return unicode(self)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'{} [{}]'.format(self.__class__.__name__, self._dict_string())

    @classmethod
    def is_like(cls, obj):
        """Checks if the object is like the current class
           If it has everything a duck has, then it's good."""
        for key in cls._attrs():
            if not hasattr(obj, key):
                return False
        return True

class Position(StructureBase):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        other = Position.from_value(other)
        return Position(self.x+other.x, self.y+other.y)

    def __sub__(self, other):
        other = Position.from_value(other)
        return Position(self.x-other.x, self.y-other.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not(self == other)

    @classmethod
    def from_value(cls, value):
        if not value:
            return cls()
        if cls.is_like(value):
            return value
        elif len(value) >= 2:
            return cls(value[0], value[1])
        else:
            return cls()


class Size(StructureBase):
    def __init__(self, width=0, height=0):
        self.height = height
        self.width = width

    def __add__(self, other):
        other = Size.from_value(other)
        return Size(self.width+other.width, self.height+other.height)

    def __sub__(self, other):
        other = Size.from_value(other)
        return Size(self.width-other.width, self.height-other.height)

    def __eq__(self, other):
        return self.width == other.width and self.height == other.height

    def __ne__(self, other):
        return not(self == other)

    @classmethod
    def from_value(cls, value):
        if not value:
            return cls()
        if cls.is_like(value):
            return value
        elif len(value) >= 2:
            return cls(value[0], value[1])
        else:
            return cls()


class Rectangle(StructureBase):
    def __init__(self, position=None, size=None):
        """ A rectangle object with coordinates and size.
        position: can take the first two values of an array or a Position object
        size: can take the first two values of an array or a Size object
        """
        self._position = None
        self._size = None
        self.position = position
        self.size = size

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = Position.from_value(position)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = Size.from_value(size)

    def intersects_with(self, position):
        """Checks if the position is within the bounds of the rectangle including the edges"""
        pos = Position.from_value(position)
        if pos.x < self.position.x + self.size.width and\
           pos.x >= self.position.x:
               if pos.y < self.position.y + self.size.height and\
                  pos.y >= self.position.y:
                      return True
        return False

