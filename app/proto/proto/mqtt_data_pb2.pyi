from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FieldValue(_message.Message):
    __slots__ = ("field_name", "string_value", "int_value", "float_value", "bool_value", "json_value", "timestamp")
    FIELD_NAME_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    FLOAT_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    JSON_VALUE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    field_name: str
    string_value: str
    int_value: int
    float_value: float
    bool_value: bool
    json_value: bytes
    timestamp: int
    def __init__(self, field_name: _Optional[str] = ..., string_value: _Optional[str] = ..., int_value: _Optional[int] = ..., float_value: _Optional[float] = ..., bool_value: bool = ..., json_value: _Optional[bytes] = ..., timestamp: _Optional[int] = ...) -> None: ...

class DetailData(_message.Message):
    __slots__ = ("topic", "message_id", "timestamp", "fields", "metadata")
    class MetadataEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TOPIC_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FIELDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    topic: str
    message_id: str
    timestamp: int
    fields: _containers.RepeatedCompositeFieldContainer[FieldValue]
    metadata: _containers.ScalarMap[str, str]
    def __init__(self, topic: _Optional[str] = ..., message_id: _Optional[str] = ..., timestamp: _Optional[int] = ..., fields: _Optional[_Iterable[_Union[FieldValue, _Mapping]]] = ..., metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class FieldMapping(_message.Message):
    __slots__ = ("mqtt_field", "db_column", "data_type", "save_to_detail")
    MQTT_FIELD_FIELD_NUMBER: _ClassVar[int]
    DB_COLUMN_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    SAVE_TO_DETAIL_FIELD_NUMBER: _ClassVar[int]
    mqtt_field: str
    db_column: str
    data_type: str
    save_to_detail: bool
    def __init__(self, mqtt_field: _Optional[str] = ..., db_column: _Optional[str] = ..., data_type: _Optional[str] = ..., save_to_detail: bool = ...) -> None: ...

class MappingConfig(_message.Message):
    __slots__ = ("topic_name", "target_table", "mappings", "version")
    TOPIC_NAME_FIELD_NUMBER: _ClassVar[int]
    TARGET_TABLE_FIELD_NUMBER: _ClassVar[int]
    MAPPINGS_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    topic_name: str
    target_table: str
    mappings: _containers.RepeatedCompositeFieldContainer[FieldMapping]
    version: int
    def __init__(self, topic_name: _Optional[str] = ..., target_table: _Optional[str] = ..., mappings: _Optional[_Iterable[_Union[FieldMapping, _Mapping]]] = ..., version: _Optional[int] = ...) -> None: ...
