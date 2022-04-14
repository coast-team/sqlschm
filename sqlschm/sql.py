from dataclasses import dataclass
from enum import Enum, auto
from collections.abc import Sequence


class _ReprEnum(Enum):
    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


# SQLite specific
class Dialect(_ReprEnum):
    SQLITE = auto()


# SQLite specific
class OnConflict(_ReprEnum):
    ABORT = auto()
    FAIL = auto()
    IGNORE = auto()
    REPLACE = auto()
    ROLLBACK = auto()


ON_CONFLICT: frozenset[str] = frozenset(member.name for member in OnConflict)


class OnUpdateDelete(_ReprEnum):
    CASCADE = auto()
    NO_ACTION = auto()
    RESTRICT = auto()
    SET_DEFAULT = auto()
    SET_NULL = auto()


class Sorting(_ReprEnum):
    ASC = auto()
    DESC = auto()


"""
From the most specific to the least specific.
e.g. database.schema.table is represented as ("table", "schema", "database")
"""
QualifiedName = Sequence[str]


@dataclass(frozen=True, kw_only=True, slots=True)
class Type:
    name: str
    params: Sequence[int] = tuple()


@dataclass(frozen=True, kw_only=True, slots=True)
class Default:
    pass


@dataclass(frozen=True, kw_only=True, slots=True)
class Column:
    name: str
    type: Type
    not_null: bool = False
    autoincrement: bool = False
    generated: bool = False
    default: Default | None = None
    collation: str | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class ConstraintEnforcement:
    initially_deferred: bool = False
    not_deferrable: bool = False


@dataclass(frozen=True, kw_only=True, slots=True)
class Indexed:
    column: str
    collation: str | None = None
    sorting: Sorting | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Uniqueness:
    name: str | None = None
    indexed: Sequence[Indexed]
    is_primary: bool = False
    on_conflict: OnConflict = OnConflict.ABORT


@dataclass(frozen=True, kw_only=True, slots=True)
class ForeignKey:
    name: str | None = None
    columns: Sequence[str]
    foreign_table: QualifiedName
    referred_columns: Sequence[str] | None = None
    on_delete: OnUpdateDelete = OnUpdateDelete.NO_ACTION
    on_update: OnUpdateDelete = OnUpdateDelete.NO_ACTION
    enforcement: ConstraintEnforcement


Constraint = Uniqueness | ForeignKey


@dataclass(frozen=True, kw_only=True, slots=True)
class TableOptions:
    strict: bool = False
    without_rowid: bool = False


@dataclass(frozen=True, kw_only=True, slots=True)
class Table:
    name: QualifiedName
    columns: Sequence[Column]
    constraints: Sequence[Constraint]
    options: TableOptions = TableOptions()
    if_not_exists: bool = False
    or_replace: bool = False
    temporary: bool = False


@dataclass(frozen=True, kw_only=True, slots=True)
class Schema:
    tables: Sequence[Table]
