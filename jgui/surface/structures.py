import colorsys

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

    def _dict_items(self):
        for a in reversed(self._attrs()):
            yield a, getattr(self,a)

    def _dict_string(self):
        return ', '.join('{}={}'.format(key, val) for key, val in self._dict_items())

    def __repr__(self):
        return unicode(self)

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __unicode__(self):
        return u'{} [{}]'.format(self.__class__.__name__, self._dict_string())

    def __eq__(self, other):
        eq = True
        for attr in self._attrs():
            val = getattr(self, attr)
            if hasattr(other, attr):
                eq &= getattr(other, attr) == val
            else:
                return False
        return eq

    def __getitem__(self, index):
        return list(self)[index]

    def __len__(self):
        return len(self._attrs())

    def __ne__(self, other):
        return not(self == other)

    @classmethod
    def is_like(cls, obj):
        """Checks if the object is like the current class
           If it has everything a duck has, then it's good."""
        for key in cls._attrs():
            if not hasattr(obj, key):
                return False
        return True

    @classmethod
    def from_value(cls, value):
        try:
            return cls(*value)
        except TypeError:
            return cls()

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

    def __iter__(self):
        yield self.x
        yield self.y


class Size(StructureBase):
    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height

    def __add__(self, other):
        other = Size.from_value(other)
        return Size(self.width+other.width, self.height+other.height)

    def __sub__(self, other):
        other = Size.from_value(other)
        return Size(self.width-other.width, self.height-other.height)

    def __iter__(self):
        yield self.width
        yield self.height


class Color(StructureBase):
    def __init__(self, r=0, g=0, b=0, a=1):
        self.r = float(r)
        self.g = float(g)
        self.b = float(b)
        self.a = float(a)

    def __add__(self, other):
        """Blend two colors using self as the background and other as the foreground"""
        other = Color.from_value(other)
        r = Color()
        r.a = 1 - (1-other.a)*(1-self.a)
        r_a_inv = self.a*(1-other.a)/r.a
        o_factor = other.a/r.a
        r.r = other.r*o_factor + self.r*r_a_inv
        r.g = other.g*o_factor + self.g*r_a_inv
        r.b = other.b*o_factor + self.b*r_a_inv
        return r

    def brightness(self, value):
        h, s, v = colorsys.rgb_to_hsv(self.r, self.g, self.b)
        v = value
        self.r, self.g, self.b = colorsys.hsv_to_rgb(h, s, v)

    def hue(self, value):
        h, s, v = colorsys.rgb_to_hsv(self.r, self.g, self.b)
        h = value
        self.r, self.g, self.b = colorsys.hsv_to_rgb(h, s, v)

    def saturation(self, value):
        h, s, v = colorsys.rgb_to_hsv(self.r, self.g, self.b)
        s = value
        self.r, self.g, self.b = colorsys.hsv_to_rgb(h, s, v)

    def from_hsv(self, h, s, v):
        self.r, self.g, self.b = colorsys.hsv_to_rgb(h, s, v)
        return self

    def __iter__(self):
        yield self.r
        yield self.g
        yield self.b
        yield self.a

    @classmethod
    def hex_to_rgba(cls, hex_val):
        """Converts a hex string in the format 0xFFAABB/CC or an integer to rgba"""
        if isinstance(hex_val, (long, int)):
            hexstring = "{0:x}".format(abs(hex_val))
        elif isinstance(hex_val, basestring):
            hexstring = hexval[2:]
        else:
            return None
        if len(hexstring) % 2 != 0:
            hexstring = '0' + hexstring
        if len(hexstring) != 6 and len(hexstring) != 8:
            return None
        ba = []
        for i in xrange(0, len(hexstring), 2):
            ba.append(int(hexstring[i:i+2], 16))
        c = cls(*ba)
        return c

    @classmethod
    def from_value(cls, value):
        try:
            return cls(*value)
        except TypeError:
            c = cls.hex_to_rgba(value)
            if c is not None:
                return c
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

    def __iter__(self):
        yield list(self.position)
        yield list(self.size)

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

