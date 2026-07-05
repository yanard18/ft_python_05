# Duck Typing vs. Abstract Base Classes (ABCs)

Welcome to the definitive guide on polymorphism in Python. This document explores the architectural differences between Duck Typing (implicit contracts) and Abstraction (explicit contracts), and helps you decide which design pattern to use for your next system.

---

## Overview

In object-oriented programming, polymorphism allows different classes to be treated as if they were the same type, as long as they share the same interface. Python offers two primary philosophies for achieving this:
1. Duck Typing: "Assume it works until it doesn't."
2. Abstract Base Classes (ABCs): "Prove you work before you start."

---

## Duck Typing (The Implicit Contract)

Duck typing gets its name from the famous "duck test":
> "If it walks like a duck and quacks like a duck, it must be a duck."

In Python, duck typing means you do not check the type of an object; you only check its behavior. If an object has the methods or attributes you need, you simply use them.

### Key Characteristics:
* No Inheritance Required: Classes are completely independent.
* Runtime Execution: Errors only occur at the exact moment a missing method is called (AttributeError).
* Flexibility: Extremely easy to swap components or create mock objects for testing.

### Example:
```python
class Duck:
    def speak(self): return "Quack!"

class Robot:
    def speak(self): return "Bzzzt!"

# The function doesn't care about the class type, only that `.speak()` exists.
def make_sound(entity):
    print(entity.speak()) 
```

---

## Abstract Base Classes (The Explicit Contract)

Abstract Base Classes (ABCs) enforce strict, nominal subtyping. By inheriting from an ABC and using the @abstractmethod decorator, you create a rigid blueprint that child classes must follow.

### Key Characteristics:
* Strict Inheritance: Child classes must inherit from the parent ABC.
* Fail-Fast Instantiation: If a child class forgets to implement a required method, Python throws a TypeError the moment you try to instantiate the object, protecting your pipeline from bad data.
* Predictability: Ideal for enterprise-scale architecture where multiple developers need to rely on guaranteed interfaces.

### Example:
```python
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def speak(self):
        pass

# This will fail upon instantiation if `speak` is not defined!
class Dog(Animal):
    def speak(self):
        return "Woof!"
```

---

## The Middle Ground: Protocols (Structural Subtyping)

Introduced in Python 3.8 (typing.Protocol), Protocols formalize duck typing for static type checkers (like mypy). They allow you to define the "shape" of an object without forcing the object to explicitly inherit from a base class. 

If a class structurally matches the Protocol (i.e., it has the right methods), it passes the type check.

```python
from typing import Protocol

class Speaker(Protocol):
    def speak(self) -> str:
        ...

class Cat:
    def speak(self) -> str:
        return "Meow!"

# A type checker knows Cat is a valid Speaker, even without inheritance!
def make_sound(entity: Speaker):
    print(entity.speak())
```

---

## Comparison Matrix

| Feature | Duck Typing | Abstract Base Classes (ABCs) | Protocols (Typing) |
| :--- | :--- | :--- | :--- |
| Validation | Implicit | Explicit | Structural |
| Inheritance | Not required | Strictly required | Not required |
| Error Timing | Execution (Runtime) | Instantiation (Runtime) | Static (Pre-run via IDE/mypy) |
| Best For | Scripts, fast prototyping | Enterprise systems, strict pipelines | Type-hinted duck typing |

---

## When to Use Which?

* Use Duck Typing when you want maximum flexibility, are writing smaller scripts, or need to quickly inject mock objects during testing.
* Use ABCs when building core internal frameworks where security and predictability are paramount, and you want objects to aggressively fail upon creation if they are missing required methods.
* Use Protocols when you want the decoupled flexibility of Duck Typing, but still want your IDE and type-checkers to warn you if you pass the wrong object to a function.
