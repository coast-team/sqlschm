from dataclasses import dataclass
from enum import Enum, auto
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
QualifiedName = tuple[str, ...]


@dataclass(frozen=True, kw_only=True, slots=True)
class Type:
    name: str
    params: tuple[int, ...] = tuple()


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
    expr: tuple[tok.Token, ...]


@dataclass(frozen=True, kw_only=True, slots=True)
class NotNull:
    name: str | None = None
    on_conflict: OnConflict | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Generated:
    name: str | None = None
    expr: tuple[tok.Token, ...]
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
    indexed: tuple[Indexed, ...]
    is_primary: bool = False
    autoincrement: bool = False
    on_conflict: OnConflict | None = None

    def columns(self, /) -> Iterable[str]:
        """Names of indexed columns"""
        return (x.column for x in self.indexed)


@dataclass(frozen=True, kw_only=True, slots=True)
class ForeignKey:
    name: str | None = None
    is_table_constraint: bool = False
    columns: tuple[str, ...]
    foreign_table: QualifiedName
    referred_columns: tuple[str, ...] | None = None
    on_delete: OnUpdateDelete | None = None
    on_update: OnUpdateDelete | None = None
    match: Match | None = None
    enforcement: ConstraintEnforcement | None = None


@dataclass(frozen=True, kw_only=True, slots=True)
class Check:
    name: str | None = None
    is_table_constraint: bool = False
    expr: tuple[tok.Token, ...]


TableConstraint = Uniqueness | ForeignKey | Check


ColumnConstraint = TableConstraint | Collation | Default | NotNull | Generated


def uniqueness(constraints: Iterable[ColumnConstraint], /) -> Iterable[Uniqueness]:
    """All uniqueness constraints, including the primary key"""
    return (x for x in constraints if isinstance(x, Uniqueness))


def primary_key(constraints: Iterable[ColumnConstraint], /) -> Uniqueness | None:
    """First found primary key constraint"""
    return next((x for x in uniqueness(constraints) if x.is_primary), None)


def foreign_keys(constraints: Iterable[ColumnConstraint], /) -> Iterable[ForeignKey]:
    """All foreign key constraints"""
    return (x for x in constraints if isinstance(x, ForeignKey))


def checks(constraints: Iterable[ColumnConstraint], /) -> Iterable[Check]:
    """All foreign key constraints"""
    return (x for x in constraints if isinstance(x, Check))


@dataclass(frozen=True, kw_only=True, slots=True)
class Column:
    name: str
    type: Type = Type(name="")
    constraints: tuple[ColumnConstraint, ...] = tuple()

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
    columns: tuple[Column, ...]
    constraints: tuple[TableConstraint, ...] = tuple()
    options: TableOptions = TableOptions()
    if_not_exists: bool = False
    or_replace: bool = False
    temporary: bool = False

    def column(self, name: str, /) -> Column | None:
        return next(x for x in self.columns if x.name == name)

    def generated_columns(self, /) -> Iterable[Column]:
        return (x for x in self.columns if x.generated() is not None)

    def non_generated_columns(self, /) -> Iterable[Column]:
        return (x for x in self.columns if x.generated() is None)

    def all_constraints(self, /) -> Iterable[TableConstraint]:
        """Constraints declared on the table and on the columns"""
        return itertools.chain(
            itertools.chain.from_iterable(
                col.table_constraints() for col in self.columns
            ),
            self.constraints,
        )

    def primary_key(self, /) -> Uniqueness | None:
        """First found primary key constraint"""
        return primary_key(self.all_constraints())

    def uniqueness(self, /) -> Iterable[Uniqueness]:
        """All uniqueness constraints, including the primary key"""
        return uniqueness(self.all_constraints())

    def foreign_keys(self, /) -> Iterable[ForeignKey]:
        """All foreign key constraints"""
        return foreign_keys(self.all_constraints())

    def checks(self, /) -> Iterable[Check]:
        """All foreign key constraints"""
        return checks(self.all_constraints())


@dataclass(frozen=True, kw_only=True, slots=True)
class Index:
    name: QualifiedName
    table: str
    indexed: tuple[Indexed, ...]
    where: tuple[tok.Token, ...] | None
    if_not_exists: bool = False
    unique: bool = False


SchemaItem = Index | Table


@dataclass(frozen=True, kw_only=True, slots=True)
class Schema:
    items: tuple[SchemaItem, ...]

    def tables(self, /) -> Iterable[Table]:
        return (x for x in self.items if isinstance(x, Table))

    def indexes(self, /) -> Iterable[Index]:
        return (x for x in self.items if isinstance(x, Index))

    def unique_indexes(self, /) -> Iterable[Index]:
        return (x for x in self.indexes() if x.unique)


Symbols = dict[str, Table]


def symbols(schema: Schema, /) -> Symbols:
    return {tbl.name[0]: tbl for tbl in schema.tables()}


def referred_columns(fk: ForeignKey, symbols: Symbols, /) -> tuple[str, ...]:
    """referred columns of `fk` or primary key of the foreign table"""
    foreign_table = symbols.get(fk.foreign_table[0])
    assert (
        foreign_table is not None
    ), f"Table '{fk.foreign_table[0]}' is not present in `symbols`"
    referred_columns = fk.referred_columns
    if referred_columns is None:
        f_pk = foreign_table.primary_key()
        assert f_pk is not None
        return tuple(f_pk.columns())
    else:
        return referred_columns


def resolve_foreign_key(
    fk: ForeignKey, col: str, symbols: Symbols
) -> Iterable[ForeignKey | str]:
    assert col in fk.columns
    foreign_table = symbols.get(fk.foreign_table[0])
    assert (
        foreign_table is not None
    ), f"Table '{fk.foreign_table[0]}' is not present in `symbols`"
    ref_cols = referred_columns(fk, symbols)
    assert len(fk.columns) == len(ref_cols)
    f_col = ref_cols[fk.columns.index(col)]
    for f_fk in foreign_table.foreign_keys():
        if f_col in f_fk.columns:
            yield f_fk
            yield from resolve_foreign_key(f_fk, f_col, symbols)
            return
    yield f_col
