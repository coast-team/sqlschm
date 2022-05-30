from dataclasses import dataclass
from enum import Enum, auto
from collections.abc import Sequence
from sqlschm import tok
from typing import Iterable
import itertools


class _ReprEnum(Enum):
    def __repr__(self) -> str:
        return f"{type(self).__name__}.{self.name}"


# SQLite specific
class Dialect(_ReprEnum):
    SQLITE = auto()


class ConstraintEnforcementTime(_ReprEnum):
    DEFERRED = auto()
    IMMEDIATE = auto()


class Match(_ReprEnum):
    FULL = auto()
    PARTIAL = auto()
    SIMPLE = auto()


MATCH: frozenset[str] = frozenset(member.name for member in Match)


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


class GeneratedKind(_ReprEnum):
    STORED = auto()
    VIRTUAL = auto()


GENERATED_KIND: frozenset[str] = frozenset(member.name for member in GeneratedKind)


"""
From the most specific to the least specific.
e.g. database.schema.table is represented as ("table", "schema", "database")
"""
QualifiedName = Sequence[str]


@dataclass(frozen=True, kw_only=True, slots=True)
class Alias:
    name: QualifiedName


@dataclass(frozen=True, kw_only=True, slots=True)
class Type:
    name: str
    params: Sequence[int] = tuple()


@dataclass(frozen=True, kw_only=True, slots=True)
class ConstraintEnforcement:
    initially: ConstraintEnforcementTime | None = None
    not_deferrable: bool = False


@dataclass(frozen=True, kw_only=True, slots=True)
class Collation:
    name: str | None = None
    value: str


@dataclass(frozen=True, kw_only=True, slots=True)
class Default:
    name: str | None = None
    expr: Sequence[tok.Token]


@dataclass(frozen=True, kw_only=True, slots=True)
class NotNull:
    name: str | None = None
    on_conflict: OnConflict | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Generated:
    name: str | None = None
    expr: Sequence[tok.Token]
    kind: GeneratedKind | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Indexed:
    column: str
    collation: Collation | None = None
    sorting: Sorting | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Uniqueness:
    name: str | None = None
    is_table_constraint: bool = False
    indexed: Sequence[Indexed]
    is_primary: bool = False
    autoincrement: bool = False
    on_conflict: OnConflict | None = None

    def columns(self, /) -> Sequence[str]:
        return [x.column for x in self.indexed]


@dataclass(frozen=True, kw_only=True, slots=True)
class ForeignKey:
    name: str | None = None
    is_table_constraint: bool = False
    columns: Sequence[str]
    foreign_table: Alias
    referred_columns: Sequence[str] | None
    on_delete: OnUpdateDelete | None = None
    on_update: OnUpdateDelete | None = None
    match: Match | None = None
    enforcement: ConstraintEnforcement | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Check:
    name: str | None = None
    is_table_constraint: bool = False
    expr: Sequence[tok.Token]


TableConstraint = Uniqueness | ForeignKey | Check


ColumnConstraint = TableConstraint | Collation | Default | NotNull | Generated


@dataclass(frozen=True, kw_only=True, slots=True)
class Column:
    name: str
    type: Type
    constraints: Sequence[ColumnConstraint]

    def collation(self, /) -> Collation | None:
        return next((x for x in self.constraints if isinstance(x, Collation)), None)

    def default(self, /) -> Default | None:
        return next((x for x in self.constraints if isinstance(x, Default)), None)

    def generated(self, /) -> Generated | None:
        return next((x for x in self.constraints if isinstance(x, Generated)), None)

    def not_null(self, /) -> NotNull | None:
        return next((x for x in self.constraints if isinstance(x, NotNull)), None)

    def table_constraints(self, /) -> Iterable[TableConstraint]:
        return (
            x
            for x in self.constraints
            if isinstance(x, Uniqueness)
            or isinstance(x, ForeignKey)
            or isinstance(x, Check)
        )


@dataclass(frozen=True, kw_only=True, slots=True)
class TableOptions:
    strict: bool = False
    without_rowid: bool = False


@dataclass(frozen=True, kw_only=True, slots=True)
class Table:
    name: QualifiedName
    columns: Sequence[Column]
    constraints: Sequence[TableConstraint]
    options: TableOptions = TableOptions()
    if_not_exists: bool = False
    or_replace: bool = False
    temporary: bool = False

    def all_constraints(self, /) -> Iterable[TableConstraint]:
        return itertools.chain(
            itertools.chain.from_iterable(
                col.table_constraints() for col in self.columns
            ),
            self.constraints,
        )

    def primary_key(self, /) -> Uniqueness | None:
        """First found primary key constraint"""
        return next(
            (
                x
                for x in self.all_constraints()
                if isinstance(x, Uniqueness) and x.is_primary
            ),
            None,
        )

    def uniqueness(self, /) -> list[Uniqueness]:
        """All uniqueness constraints, including the primary key"""
        return [x for x in self.all_constraints() if isinstance(x, Uniqueness)]

    def foreign_keys(self, /) -> list[ForeignKey]:
        """All foreign key constraints"""
        return [x for x in self.all_constraints() if isinstance(x, ForeignKey)]

    def checks(self, /) -> list[Check]:
        """All foreign key constraints"""
        return [x for x in self.all_constraints() if isinstance(x, Check)]


@dataclass(frozen=True, kw_only=True, slots=True)
class Schema:
    tables: Sequence[Table]


Symbols = dict[str, Table]


def symbols(schema: Schema, /) -> Symbols:
    return dict((tbl.name[0], tbl) for tbl in schema.tables)
