"""
Implements interaction with Spotify over DBus
TODO Cast arguments and return values
"""

import dbus
from xml.etree import ElementTree


object_path = '/org/mpris/MediaPlayer2'
service = 'org.mpris.MediaPlayer2.spotify'


def changeType(dbusTypeName, value):
    """
    BYTE		y (121)	Unsigned 8-bit integer
    BOOLEAN		b (98)	Boolean value: 0 is false, 1 is true, any other value allowed by the marshalling format is invalid
    INT16		n (110)	Signed (two's complement) 16-bit integer
    UINT16		q (113)	Unsigned 16-bit integer
    INT32		i (105)	Signed (two's complement) 32-bit integer
    UINT32		u (117)	Unsigned 32-bit integer
    INT64		x (120)	Signed (two's complement) 64-bit integer (mnemonic: x and t are the first characters in "sixty" not already used for something more common)
    UINT64		t (116)	Unsigned 64-bit integer
    DOUBLE		d (100)	IEEE 754 double-precision floating point
    UNIX_FD		h (104)	Unsigned 32-bit integer representing an index into an out-of-band array of file descriptors, transferred via some platform-specific mechanism (mnemonic: h for handle)
    STRING		s (115)	No extra constraints
    OBJECT_PATH	o (111)	Must be a syntactically valid object path
    SIGNATURE	g (103)	Zero or more single complete types

    :param dbusTypeName:
    :param value:
    :return:
    """
    types = {
        'y': lambda x: x,
        'b': lambda x: x,
        'n': lambda x: x,
        'q': lambda x: x,
        'i': lambda x: x,
        'u': lambda x: x,
        'x': lambda x: x,
        't': lambda x: x,
        'd': lambda x: x,
        'h': lambda x: x,
        's': lambda x: str(x),
        'o': lambda x: x,
        'g': lambda x: x
    }


class Method:
    """
    Describes a method available on DBus
    """
    def __init__(self, interface_name, method_name, args, response):
        """
        :param interface_name: DBus interface that contains the method
        :param method_name:  The method name to call
        :param args:  Arguments to pass to method
        :param response: Expected DBus response
        """
        self.interface_name = interface_name
        self.method_name = method_name
        self.args = args
        self.response = response


class Arg:
    """
    Describe an argument to be passed into a DBus method
    """
    def __init__(self, name, dbus_type):
        """
        :param name: Name of the argument
        :param dbus_type: Type of the argument expected by DBus
        """
        self.dbus_type = dbus_type
        self.name = name


class Response:
    """
    Describe the response from a DBus method
    """
    def __init__(self, name, dbus_type):
        """
        :param name: The name of the response
        :param dbus_type: Type of response
        """
        self.dbus_type = dbus_type
        self.name = name


class Property:
    """
    Describe a property available on DBus
    """
    def __init__(self, interface_name, property_name, dbus_type, access):
        """
        :param interface_name: DBus interface that contains the property
        :param property_name: The name of the property
        :param dbus_type: DBus type of the property
        :param access: Access level (read, readwrite)
        """
        self.interface_name = interface_name
        self.name = property_name
        self.dbus_type = dbus_type
        self.access = access


class SpotifyDbus:
    """
    Class responsible for communicating with Spotify via DBus.

    Hides all knowledge of interfaces exposing only "commands" which can either
    be methods or parameters.

    Not all properties and methods have been implemented by Spotify, although
    all are available here.
    """
    def __init__(self, logging):
        logging.info("Building SpotifyDbus")
        self.logging = logging
        self.bus = dbus.SessionBus()
        self.bus_object = self.bus.get_object(service, object_path)
        self.methods = []
        self.properties = []

        logging.info("Introspecting methods and properties from DBus")
        iface = dbus.Interface(self.bus_object, 'org.freedesktop.DBus.Introspectable')
        xml_string = iface.Introspect()
        node = ElementTree.fromstring(xml_string)
        for interface in node:
            # Only care about interfaces
            if interface.tag == 'interface':
                for attribute in interface:
                    if attribute.tag == 'method':
                        args = []
                        for parameters in attribute:
                            if parameters.attrib['direction'] == 'in':
                                args.append(Arg(parameters.attrib['name'], parameters.attrib['type']))
                            if parameters.attrib['direction'] == 'out':
                                response = Response(parameters.attrib['name'], parameters.attrib['type'])
                        self.methods.append(Method(interface.attrib['name'], attribute.attrib['name'], args, response))
                    if attribute.tag == 'property':
                        self.properties.append(Property(interface.attrib['name'], attribute.attrib['name'], attribute.attrib['type'], attribute.attrib['access']))
                    if attribute.tag == 'signal':
                        # Currently not handing signals
                        pass
        logging.info("Completed introspection")

    def print_commands(self):
        """
        Prints all available method and properties as signatures
        :return: None
        """
        print('print_commands() -> commands: s')

        for method in self.methods:
            method_description = method.method_name + '('
            for arg in method.args:
                method_description += arg.name + ': ' + arg.dbus_type + ', '
            method_description = method_description.strip(', ') + ')'
            method_description += ' -> ' + method.response.name + ': ' + method.response.dbus_type
            print(method_description)

        for property in self.properties:
            property_description = property.name + ' -> ' + property.dbus_type + ' (' + property.access + ')'
            print(property_description)

    def find_dbus_method(self, name):
        """
        Find a method by name.
        :param name: Name of method to search for.
        :return: Method or None
        """
        try:
            return next(method for method in self.methods if method.method_name == name)
        except StopIteration:
            return None

    def has_dbus_method(self, name):
        """
        Check if a method exists.
        :param name: Name of method to search for.
        :return: True if method exists
        """
        return self.find_dbus_method(name) is not None

    def call_dbus_method(self, method, args=None):
        """
        Call a method on the DBus either using a Method class or string name of
        the method
        :param method: Method call or string name of method
        :param args: Optional arguments to pass to method
        :return: Any response from the DBus
        """
        if args is None:
            args = []

        if isinstance(method, str):
            method = self.find_dbus_method(method)

        self.logging.info('Calling method \'{}\' on interface \'{}\''.format(method.method_name, method.interface_name))
        iface = dbus.Interface(self.bus_object, method.interface_name)
        iface_method = getattr(iface, method.method_name)
        return iface_method(*args)

    def find_dbus_property(self, name):
        """
        Find a property by name.
        :param name: Name of property to search for.
        :return: Property or None
        """
        try:
            return next(property for property in self.properties if property.name == name)
        except StopIteration:
            return None

    def has_dbus_property(self, name):
        """
        Check if property exists.
        :param name: Name of property to search for.
        :return: True if method exists.
        """
        return self.find_dbus_property(name) is not None

    def get_dbus_property(self, property):
        """
        Get a property from the DBus either using Property class or string name
        of the property
        :param property: Property class or string name of property
        :return: Property from DBus if any
        """
        if isinstance(property, str):
            property = self.find_dbus_property(property)

        self.logging.info('Getting property \'{}\' from interface \'{}\''.format(property.name, property.interface_name))
        iface = dbus.Interface(self.bus_object, 'org.freedesktop.DBus.Properties')
        return iface.Get(property.interface_name, property.name)

    def set_dbus_property(self, property, value):
        """
        Set a property on the DBus either using Property class or string name
        of the property
        :param property: Property class or string name of property
        :param value: Value to set
        :return: Return from DBus if any
        """
        if isinstance(property, str):
            property = self.find_dbus_property(property)

        self.logging.info('Setting property \'{}\' on interface \'{}\' to \'{}\''.format(property.name, property.interface_name, value))
        iface = dbus.Interface(self.bus_object, 'org.freedesktop.DBus.Properties')
        return iface.Set(property.interface_name, property.name, value)

    def get_spotify_metadata(self, name):
        """
        Get value from Metadata
        :param name: Metadata name, with or without 'descriptor:' prefix
        :return: Metadata value or None
        """
        metadata = self.get_dbus_property('Metadata')

        if name in metadata:
            return metadata[name]

        for key in metadata:
            # Metadata is in format descriptor:name, ignore descriptor
            if key.split(':')[1] == name:
                return metadata[key]

        return None

    def __getattribute__(self, name):
        """
        Allow calling methods or getting properties or Metadata from the DBus
        as if they were attributes of this class
        :param name: Name of method or property
        :return: Attribute, method, property or Metadata if present
        """
        try:
            # Actual attributes of the class take priority
            return super(SpotifyDbus, self).__getattribute__(name)
        except AttributeError:
            pass

        if self.has_dbus_method(name):
            def wrapper(*args):
                return self.call_dbus_method(name, args)

            return wrapper

        if self.has_dbus_property(name):
            return self.get_dbus_property(name)

        metadata_value = self.get_spotify_metadata(name)
        if metadata_value is not None:
            return metadata_value

        return super(SpotifyDbus, self).__getattribute__(name)

    def __setattr__(self, name, value):
        """
        Allow setting of DBus properties as if they were attributes of this
        class
        :param name: Name of attribute
        :param value: Value to set it to
        :return: Property or attribute
        """
        # Check properties exists before trying to read them
        if 'properties' in self.__dict__ and self.has_dbus_property(name):
            # Allow DBus to raise exception if property is not writable
            self.set_dbus_property(name, value)

        super(SpotifyDbus, self).__setattr__(name, value)
