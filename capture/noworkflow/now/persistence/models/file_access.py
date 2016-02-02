# Copyright (c) 2016 Universidade Federal Fluminense (UFF)
# Copyright (c) 2016 Polytechnic Institute of New York University.
# This file is part of noWorkflow.
# Please, consult the license terms in the LICENSE file.
"""File Access Model"""
from __future__ import (absolute_import, print_function,
                        division, unicode_literals)

from sqlalchemy import Column, Integer, Text, TIMESTAMP
from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint

from ...utils.prolog import PrologDescription, PrologTrial, PrologAttribute
from ...utils.prolog import PrologRepr, PrologTimestamp, PrologNullable
from ...utils.prolog import PrologNullableRepr

from .base import AlchemyProxy, proxy_class, backref_one


@proxy_class
class FileAccess(AlchemyProxy):
    """Represent a file access"""

    __tablename__ = "file_access"
    __table_args__ = (
        PrimaryKeyConstraint("trial_id", "id"),
        ForeignKeyConstraint(["trial_id", "function_activation_id"],
                             ["function_activation.trial_id",
                              "function_activation.id"], ondelete="CASCADE"),
        ForeignKeyConstraint(["trial_id"], ["trial.id"], ondelete="CASCADE"),
    )
    trial_id = Column(Integer, index=True)
    id = Column(Integer, index=True)                                             # pylint: disable=invalid-name
    name = Column(Text)
    mode = Column(Text)
    buffering = Column(Text)
    content_hash_before = Column(Text)
    content_hash_after = Column(Text)
    timestamp = Column(TIMESTAMP)
    function_activation_id = Column(Integer, index=True)

    trial = backref_one("trial")  # Trial.file_accesses
    activation = backref_one("activation")  # Activation.file_accesses

    prolog_description = PrologDescription("access", (
        PrologTrial("trial_id"),
        PrologAttribute("id", fn=lambda obj: "f{}".format(obj.id)),
        PrologRepr("name"),
        PrologRepr("mode"),
        PrologNullableRepr("content_hash_before"),
        PrologNullableRepr("content_hash_after"),
        PrologTimestamp("timestamp"),
        PrologNullable("activation_id", attr_name="function_activation_id"),
    ))

    @property
    def stack(self):
        """Return the activation stack since the beginning of execution"""
        stack = []
        activation = self.activation
        while activation:
            name = activation.name
            activation = activation.caller
            if activation:
                stack.insert(0, name)
        if not stack or stack[-1] != "open":
            stack.append(" ... -> open")
        return " -> ".join(stack)

    def __key(self):
        return (self.name, self.content_hash_before, self.content_hash_after)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return (
            (self.content_hash_before == other.content_hash_before)
            and (self.content_hash_after == other.content_hash_after)
        )

    def show(self, _print=print):
        """Show object

        Keyword arguments:
        _print -- custom print function (default=print)
        """
        _print("""\
            Name: {f.name}
            Mode: {f.mode}
            Buffering: {f.buffering}
            Content hash before: {f.content_hash_before}
            Content hash after: {f.content_hash_after}
            Timestamp: {f.timestamp}
            Function: {f.stack}\
            """.format(f=self))

    def __repr__(self):
        return "FileAccess({0.trial_id}, {0.id}, {0.name}, {0.mode})".format(
            self)