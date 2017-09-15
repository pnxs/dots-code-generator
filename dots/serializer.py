import asyncio
import socket
import enum
from datetime import datetime, timedelta

def to_map(obj):
    if not obj.__dots_object__:
        raise Exception("Not a DOTS object")

    ret = {}

    for tag in obj._dots_tags:
        value = getattr(obj, obj._dots_tags[tag])
        if not value is None:
            ret[tag] = value
        print("Tag", value)

    return ret

def from_list(data, obj):
    print("FromList:")
    print("Data:", data)
    print("Obj:", obj)

    ret = []

    for item in data:
        print("Item: ", item)
        instance = obj()
        ret.append(instance)

    return ret

def from_map(data, obj):
    if not obj.__dots_object__:
        raise Exception("Not a DOTS object")

    for tag in data:
        attr = obj.__dots_attributes__[tag]
        name = attr["name"]
        value = data[tag]
        if "vector" in attr:
            print("Decode vector")
            value = from_list(data[tag], attr["class"])

        #print("Intag: ", tag, name, value)
        setattr(obj, name, value)

def deserialize_list(data, obj, list_type):
    #print("deser list:", data, obj)

    for item in data:
        #print("Item: ", item)
        instance = list_type()
        deserialize_value(item, instance)
        obj.append(instance)

def deserialize_enum(data, enumType):
    #print("deser enum:", data, enumType)
    return enumType(enumType.__dots_enum__[data])

def deserialize_value(data, obj):
    objType = type(obj)
    #print("Deser value data=%s attr=%s" % (data, objType))
    if objType in (int, str, float, bool):
        return objType(data)

    else:
        return deserialize_object(data, obj)

def deserialize_timedate(data, type):
    return None

def deserialize_object(data, obj):
    #print("deser object")
    if not obj.__dots_object__:
        raise Exception("Not a DOTS object")

    for tag in data:
        attr = obj.__dots_attributes__[tag]
        name = attr["name"]
        if attr["class"] is not None:
            #print("Attr: ", attr["name"], attr["class"].__class__)
            attrType = attr["class"]
            attrData = data[tag]
            instance = None
            if attrType == list:
                instance = attrType()
                deserialize_list(attrData, instance, attr["list_type"])
            elif issubclass(attrType, enum.Enum):
                instance = deserialize_enum(attrData, attrType)
            elif issubclass(attrType, datetime):
                instance = deserialize_timedate(attrData, attrType)
            else:
                instance = attrType()
                instance = deserialize_value(attrData, instance)
            setattr(obj, name, instance)
    return obj

def serialize_list(value):
    #print("Ser list:", value)

    ret = []

    for item in value:
        ret.append(serialize_value(item))
    return ret

def serialize_enum(value):
    #print("Ser enum:", value)
    return value.__dots_enum__[value.value]

def serialize_value(value):
    #print("ser value:", value, type(value))
    attrType = type(value)
    if attrType == list:
        return serialize_list(value)
    elif issubclass(attrType, enum.Enum):
        return serialize_enum(value)
    elif attrType in (int, str, float, bool):
        return value
    else:
        return serialize_object(value)

def serialize_object(obj):
    if not obj.__dots_object__:
        raise Exception("Not a DOTS object")

    properties = obj.__dots_attributes__

    ret = {}

    for tag in properties:
        property = properties[tag]
        propname = property["name"]
        propValue = getattr(obj, propname)

        #print("item:", propname, propValue)

        if propValue is not None:
            ret[tag] = serialize_value(propValue)

        #print("Tag:", tag, propValue)

    return ret

