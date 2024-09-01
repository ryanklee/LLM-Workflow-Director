import pytest
from src.constraint_engine import ConstraintEngine, Constraint

def test_constraint_engine_initialization():
    engine = ConstraintEngine()
    assert isinstance(engine, ConstraintEngine)
    assert len(engine.constraints) == 0

def test_add_constraint():
    engine = ConstraintEngine()
    constraint = Constraint("test", "Test constraint", lambda state: (True, ""))
    engine.add_constraint(constraint)
    assert "test" in engine.constraints
    assert engine.constraints["test"] == constraint

def test_remove_constraint():
    engine = ConstraintEngine()
    constraint = Constraint("test", "Test constraint", lambda state: (True, ""))
    engine.add_constraint(constraint)
    engine.remove_constraint("test")
    assert "test" not in engine.constraints

def test_validate_all_pass():
    engine = ConstraintEngine()
    engine.add_constraint(Constraint("test1", "Test 1", lambda state: (True, "")))
    engine.add_constraint(Constraint("test2", "Test 2", lambda state: (True, "")))
    valid, violations = engine.validate_all({})
    assert valid
    assert len(violations) == 0

def test_validate_all_fail():
    engine = ConstraintEngine()
    engine.add_constraint(Constraint("test1", "Test 1", lambda state: (True, "")))
    engine.add_constraint(Constraint("test2", "Test 2", lambda state: (False, "Failed")))
    valid, violations = engine.validate_all({})
    assert not valid
    assert len(violations) == 1
    assert "test2" in violations[0]
