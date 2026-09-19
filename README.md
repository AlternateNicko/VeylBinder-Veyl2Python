# VeylBinder-Veyl2Python

install the following required repository if you don't have already
‎[VeylPL](https://github.com/AlternateNicko/Veyl-Programming-Language)

## Description
‎Veylbinder is the main official API module for the expiremental programming language, Veyl.
It connects both Python and Veyl and can integrate Veyl objects (Variables, Functions, Classes) into python programs, and same goes for python objects integrated to Veyl as its built ins.
‎veylbinder.py is the main API program, and there is 2 main classes of this module.
- internal - accesses Veyl internal data, mostly requires a VEY object (which is the name of the class of the Veyl interpreter) that has already been executed, this can access variables, objects, functions, classes, and even integrated custom modules.
- external - this isn't for accessing, but to integrate python to your Veyl programs.
‎This is an easy module/application that lets you change configurations and save/load these configs for future uses.
‎This is then extracted and integrated.

‎there are also other features that helps you and your program.
‎- GetFunction - gets a Veyl function and transforms it into python callables. With functional return values
- GetClass - gets a Veyl class that can be instantiated to multiple objects, called, and accessed
- GetObject - gets a Veyl object that can get and set its attributes and call methods (all are only if they are publicly accessible)
- include - not used for calling, but as a decorator/wrapper on a function or a class, this integrates it immidietly to a data as it is getting defined.
- include.data - gets the Python function immidietly and you can set it up in configurations (or the external class)
‎
## How to setup
To setup veylbinder, you need to install this repositories releases (mostly the release of the version update of veyl that it supports)
‎and of course include VeylPL, or the programming langauges main directory, and must be strictly named VeylPL.
After installing, you must only move/copy veylbinder.py and move it to your project directory, and must have VeylPL anywhere, either in or out of the project folder.
‎Setup example:
```python
‎import veylbinder # entire module
‎from veylbinder import internal # internal class
‎from veylbinder import external # external class
‎from veylbinder import GetFunction # GetFunction class
‎from veylbinder import GetClass # GetClass class
‎from veylbinder import GetObject # GetObject class
‎from veylbinder import include # wrapper
```

‎your project tree should look like this
‎/VeylPL
├──...
‎/MyProject
‎├── veylbinder.py
├── myprogram.py
├── program.vey

your veyl program must also be ready (either in multi lined strings, preferably raw strings, or as a program file under .vey) and must follow veyl's own syntax
‎Example code:
```
output("Hello, World!")
```

## How to use
There is multiple classes and sub classes, but the important is internal and external.
### internal
• key methods:
- execute(code, api_library: dict = {})
- adv_execute(programs: list, api_library: dict = {}, raise_error: bool = False, get_function: list = [], get_variable: list = [], get_class: list = [])
- call_function(veyl_object, name: str, arguments: list = [])
- init_class(veyl_object, name: str, arguments: list = [])
- call_method(veyl_object, class_name: str, method_name: str, arguments: list = [])
- call_library(veyl_object, code_line: str) --- call_library is more of a standard/arbitrary code or expression format
- get_variable(veyl_object, name)
- get_function(veyl_object, name) - a call object
‎    get_function().call(parameters: list = [])
‎    get_function().next(parameters: list = [])
- get_class(veyl_object, name)
‎    get_class().const(parameters: list = [])
‎    get_class().call_method(parameters: list = [])
‎    get_class().inject_inherits(class_name: str)
‎    get_class().hasattr(name)
‎    get_class().getattr(name)
‎
- haslibrary(vey, name: str) 
- getlibrary(vey, name: str) # only works with injected libraries with an asisgned module
- path(vey)
- filename(vey)
- extension(vey)
- hasvariable(vey, name: str)
‎      
• tools:
- eval(expression, [globals, [locals]], arbitrary=True)
- special_split(line, target, left_delimeter, right_delimeter, length=-1, range=[0, -1])
- special_find(line, target, left_delimeter, right_delimeter, length=-1, range=[0, -1])
- ultimate_split(line, delimeter_targets)
‎
### external:
‎• initailizer:
- init(veyl_object)
‎• binder/access:
- bind_function(name: str, function_object: object)
- bind_class(name: str, class_object)
- bind_object(name: str, object_name: object)
- assign_variable(name: str, variable_value)
- inject_library(name: str, library_object)
‎• configurations:
- set_config(name, value)
- remove_config(name: str)
- get_config(name: str)
- config_default()
- config_save(filename: str, [path=Path.cwd()])
- config_load(path: str)
- return_config()
### GetFunction:
```python
‎func_name = veylbinder.GetFunction(name)
‎func_name()
‎variable = func_name()
```
### GetClass:
```python
‎class_name = veylbinder.GetClass(name)
‎obj = class_name(...)
‎obj.method(...)
‎variable = obj.method(...)
‎obj.variable = ...
‎print(obj.variable)
```
### GetObject:
```python
‎obj = veylbinder.GetObject(name)
‎obj.method(...)
‎variable = obj.method(...)
‎obj.variable = ...
‎print(obj.variable)
```
### include:
```python
‎@veylbinder.include
‎def function(args):
‎    ...
‎
‎metadata = veybinder.include.data
‎veylbinder.include.remove(name)
‎veylbinder.include.reset
```
‎
‎
