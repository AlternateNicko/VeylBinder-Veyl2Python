import sys

import VeylPL.veylIO
#from VeylPL.veyl import VEY # Must have the directory named VeylPL
from VeylPL.veyl import VEY
from VeylPL import syntax_encloser
from VeylPL import resolve_external
from pathlib import Path
import os
import json

def load_file(file):
    with open(file, "r") as file:
        return json.load(file)

class internal:
    """
    This is associated for Veyl Programming Language that I am working on.
    This class focuses on main code execution, calling functons, and accessing classes, but still requires complex access due to some returning metadatas.
    This mostly focuses on the main interpreter
    key methods:
        - execute(code, api_library: dict = {})
        - adv_execute(programs: list, api_library: dict = {}, raise_error: bool = False, get_function: list = [], get_variable: list = [], get_class: list = [])
        - call_function(veyl_object, name: str, arguments: list = [])
        - init_class(veyl_object, name: str, arguments: list = [])
        - call_method(veyl_object, class_name: str, method_name: str, arguments: list = [])
        - call_library(veyl_object, code_line: str) --- call_library is more of a standard/arbitrary code or expression format
        - get_variable(veyl_object, name)
        - get_function(veyl_object, name) - a call object
            get_function().call(parameters: list = [])
            get_function().next(parameters: list = [])
        - get_class(veyl_object, name)
            get_class().const(parameters: list = [])
            get_class().call_method(parameters: list = [])
            get_class().inject_inherits(class_name: str)
            get_class().hasattr(name)
            get_class().getattr(name)
            
        - haslibrary(vey, name: str) 
        - getlibrary(vey, name: str) # only works with injected libraries with an asisgned module
        - path(vey)
        - filename(vey)
        - extension(vey)
        - hasvariable(vey, name: str)
        
        tools, use helper functions used in veyl
        - eval(expression, [globals, [locals]], arbitrary=True)
        - special_split(line, target, left_delimeter, right_delimeter, length=-1, range=[0, -1])
        - special_find(line, target, left_delimeter, right_delimeter, length=-1, range=[0, -1])
        - ultimate_split(line, delimeter_targets)
        
    Note: All arguments that requires names to access Veyl defined must be strings.
    some requires a defined VEY object, instantiated either doing it manually or using
    """
    class get_function:
        def __init__(self, vey, name):
            if not isinstance(vey, VEY):
                raise TypeError("given object is not an instance of VEY")
            elif not name in vey.functions.keys():
                raise NameError("given function name is not defined")
            self.program = vey
            self.program.cnt = 0
            self.name = name
            self.function = vey.functions[name]
        
        def call(self, parameters: list = []):
            arguments = [self.program.convert_arg(arg, True) for arg in parameters]
            self.program.run_functions(self.name, arguments, False)
            if self.program.is_return:
                if len(self.program.return_val) > 1:
                    return tuple([a for a in self.program.return_val])
                return self.program.return_val[0]
            
        def next(self, parameters: list = []):
            pass # implemented once 'yield' is added
            
    class get_class:
        def __init__(self, vey, name):
            if not isinstance(vey, VEY):
                raise TypeError("given object is not an instance of VEY")
            elif not name in vey.classes.keys():
                raise NameError("given class name is not defined")
            self.program = vey
            self.name = name
            self.convert_arg = internal._convert_arg
            self.object_name = "<<external>>"
        
        def const(self, parameters: list = []):
            args = str(tuple(parameters)) if len(parameters) > 0 else "()"
            code = f"<<external>> = {self.name}{args}"
            self.program.assign_variable(code, isexternal=True)
            if self.program.is_return:
                if len(self.program.return_val) > 1:
                    return tuple([a for a in self.program.return_val])
                return self.program.return_val[0]
        
        def call(self, name: str, parameters: list = []):
            args = [self.program.convert_arg(arg, True) for arg in parameters]

            if name not in self.program.classes[self.name]["methods"].keys():
                raise NameError("given name is not a defined method for class `{self.name}`")
            t = False if self.program.classes[self.name]["methods"][name]["type"] == "pub" else True
            self.program.run_methods(self.name, name, True, self.object_name, args, t)
            if self.program.is_return:
                self.program.is_return = False
                if len(self.program.return_val) > 1:
                    return tuple([a for a in self.program.return_val])
                return self.program.return_val[0]
        
        def inject_inherits(self, child_class, parent_classes: list = []):
            pass
        
        def hasattr(self, name: str):
            if name in self.program.objects[self.object_name]["variables"]["<attr>"]:
                return True
            return False
        
        def getattr(self, name: str):
            if name in self.program.objects[self.object_name]["variables"].keys():
                result = self.program.objects[self.object_name]["variables"][name]
                return result
                
            raise AttributeError(f"{self.name} object has no attribute to {name}")
        
        def setattr(self, name: str, value):
            self.program.objects[self.object_name]["variables"][name] = value
            self.program.process_var()
    
    class get_object:
        def __init__(self, vey, name):
            if not isinstance(vey, VEY):
                raise TypeError("given object is not an instance of VEY")
            elif not name in vey.objects.keys():
                raise NameError("given class object name is not defined")
            self.program = vey
            self.name = name
            self.object = self.program.objects[name]
        
        def hasattr(self, name: str):
            if name in self.program.objects[self.object_name]["variables"]["<attr>"]:
                return True
            return False
        
        def getattr(self, name: str):
            if name in self.program.objects[self.object_name]["variables"].keys():
                result = self.program.objects[self.object_name]["variables"][name]
                return result
                
            raise AttributeError(f"{self.name} object has no attribute to {name}")
        
        def setattr(self, name: str, value):
            self.program.objects[self.object_name]["variables"][name] = value
            self.program.process_var()
            
        def call(self, method, parameters=[]):
            args = [self.program.convert_arg(arg, True) for arg in parameters]

            if method not in self.program.classes[self.name]["methods"].keys():
                raise NameError("given name is not a defined method for class `{self.name}`")
            t = False if self.program.classes[self.name]["methods"][name]["type"] == "pub" else True
            self.program.run_methods(self.name, method, True, self.object_name, args, t)
            if self.program.is_return:
                self.program.is_return = False
                if len(self.program.return_val) > 1:
                    return tuple([a for a in self.program.return_val])
                return self.program.return_val[0]
        
    @classmethod
    def _convert_arg(cls, delim: list) -> list:
        new_list = []
        for arg in delim:
            if isinstance(arg, str):
                new_list.append("'" + arg + "'")
            else:
                new_list.append(str(arg))
        return new_list
    
    @classmethod
    def execute(cls, code, api_library: dict={}):
        if not isinstance(code, str):
            raise TypeError(f"Can not execute `{type(code)}` program to VeylLang (Requires raw strings or raw multi strings)")
        elif not isinstance(api_library, dict):
            raise TypeError(f"Custom Api Libraries can not be injected, requires dict/hash map, not `{type(api_library)}` type")
        elif api_library != {} and not any(isinstance(key, str) and key is not None for key in api_library.keys()):
            raise TypeError(f"Custom Api Libraries must require string type keys")
        veyl = VEY(code, special_library=api_library)
        veyl.execute()
        return veyl
    
    @classmethod
    def adv_execute(cls, programs: list, api_library: dict={}, raise_error: bool=False, get_function: list = [], get_variable: list = [], get_class: list = []):
        if not isinstance(api_library, dict):
            raise TypeError(f"Custom Api Libraries can not be injected, requires dict/hash map, not `{type(api_library)}` type")
        elif api_library != {} and not any(isinstance(key, str) for key in api_library.keys()):
            raise TypeError(f"Custom Api Libraries must require string type keys")
        meta = {}
        for file in programs:
            if not isinstance(file, str):
                raise TypeError("Invalid string literal `{file}` for file name, must be str")
                
            path = Path(file)
            if not path.is_dir():
                raise FileNotFoundError("Given program file `{file}` is not found with in the current directory `{os.getcwd()}`")
            code = open(file, "r").read()
            veyl = VEY(code, special_library=api_library, force_raise=raise_error)
            veyl.execute()
            # gets function, variable, or list inside one metadata
            data = {
                "<main>": veyl,
                "function": None,
                "variable": None,
                "<variable info>": None,
                "class": None,
            }
            if len(get_function) > 0:
                func_data = {}
                for name in get_function:
                    func_data[name] = veyl.functions[name]
                data["function"] = func_data
            
            if len(get_variable) > 0:
                 var_data = {}
                 var_info = {}
                 obj_ref = {}
                 for name in get_variable:
                     var_data[name] = veyl.variables[name]
                     var_info[name] = veyl.variable_info[name]
                     # unusually long condition
                     if "<" + name + ">" in veyl.variables and veyl.variables["<" + name + ">"] == name and veyl.variables[name] in veyl.classes.keys():
                         obj_ref[name] = veyl.class_callers[name]
                     obj_ref[name]
                 data["variable"] = var_data
                 data["<variable info>"] = var_info
            
            if len(get_class) > 0:
                class_data = {}
                for name in get_class:
                    class_data[name] = veyl.classes[name]
                data["class"] = class_data
            
            meta[file.split(".", 1)[0].strip()] = data
        return meta
    
    @classmethod
    def call_function(cls, veyl_object, name: str, arguments: list = []):
        if not isinstance(vey, VEY):
            raise TypeError("given object is not an instance of VEY")
        elif name not in veyl_object.functions.keys():
            raise NameError("Given name is not found in available function list")
        vey.cnt = 0
        function = veyl_object.functions[name]
        arguments = [veyl_object.convert_arg(arg, True) for arg in arguments[:-1]]
        veyl_object.run_functions(name, arguments, False)
        if veyl_object.is_return:
            veyl_object.is_return = False
            if len(veyl_object.return_val) > 1:
                return tuple([a for a in veyl_object.return_val])
            return veyl_object.return_val[0]
    
    @classmethod
    def init_class(cls, vey, obj_name: str, name: str, arguments: list = []):
        if not isinstance(vey, VEY):
            raise TypeError("given object is not an instance of VEY")
        elif name not in vey.classes.keys():
            raise NameError(f"given name {name} is not a defined class")
        arguments = str(tuple(arguments))[:-2] + ")" if len(arguments) > 0 else "()"
        code = f"{obj_name} = {name}{arguments}"
        vey.assign_variable(code, isexternal=True)
        return vey
    
    @classmethod
    def call_method(cls, vey, obj_name: str, name: str, arguments: list = [], return_val: bool=False):
        if not isinstance(vey, VEY):
            raise TypeError("given object is not an instance of VEY")
        vey.cnt = 0
        arguments = str(tuple(arguments))[:-2] + ")" if len(arguments) > 0 else "()"
        
        if return_val:
            code = f"<<external>> = call {obj_name}.{name}{arguments}"
            vey.assign_variable(code, isexternal=True)
            return_value = vey.variables["<<external>>"]
            del vey.variables["<<external>>"]
            return return_value
        else:
            code = f"call {obj_name}.{name}{arguments}"
            vey.execute_functions(code)
    
    @classmethod
    def call_library(cls, vey, library_name: str, name: str, arguments: list = [], return_val: bool=False):
        if not isinstance(vey, VEY):
            raise TypeError("given object is not an instance of VEY")
        elif library_name not in vey.libraries:
            raise NameError("given library is either invalid or does not exist")
        elif library_name not in vey.library:
            raise NameError("module has not been imported yet (write an import code in the first in the program)")
        vey.cnt = 0
        arguments = cls._convert_arg(arguments)
        arguments = str(tuple(arguments))[:-2] + ")" if len(arguments) > 0 else "()"
        
        if return_val:
            code = f"<<external>> = {library_name}.{name}{arguments}"
            vey.assign_variable(code, isexternal=True)
            return_value = vey.variables["<<external>>"]
            del vey.variables["<<external>>"]
            return return_value
        else:
            code = f"{library_name}.{name}{arguments}"
            vey.execute_functions(code)
    
    @classmethod
    def get_variable(cls, vey, name):
        if not isinstance(vey, VEY):
            raise TypeError("given object is not an instance of VEY")
        if name not in vey.variables:
            raise NameError("given variable name is undefined")
        return vey.variables[name]
    
    @classmethod
    def has_variable(cls, vey, name):
        if not isinstance(vey, VEY):
            raise TypeError("given object is not an instance of VEY")
        if name not in vey.variables:
            return False
        return True
    
    @classmethod
    def has_library(cls, vey, name):
        if not isinstance(vey, VEY):
            raise TypeError("given object is not an instance of VEY")
        if name not in vey.library:
            return False
        return True
    
    @classmethod
    def get_library(cls, vey, name):
        if not isinstance(vey, VEY):
            raise TypeError("given object is not an instance of VEY")
        if name not in vey.library:
            return NameError("given library name is invalid, no instances of any imported modules named `{name}`")
        if name not in vey.nplibs.keys():
            return AttributeError("given library name is valid, but has no assigned module (It is most likely because {name} is a built in library name)")
        return vey.nplibs[name]
    
    @classmethod
    def path(cls, vey):
        return vey.path
    
    @classmethod
    def file_name(cls, vey):
        return vey.file_name
    
    @classmethod
    def file_extension(cls, vey):
        return vey.file_extension
    
    @classmethod
    def eval(cls, vey, expression: str, globals=None, locals=None, arbitrary=True):
        return vey.eval(expression, globals, locals, arbitrary)
    
    @classmethod
    def ultimate_split(cls, vey, line: str, delimeter: list | tuple, group_pairs=(("'", '"'), ('"', "'")), nest_pairs=(("(", ")"), ("[", "]"), ("{", "}")), join_capture: bool = True):
        return vey.ultimate_split(line, delimeter, group_pairs, nest_pairs, join_capture)
    
    @classmethod
    def special_split(cls, vey, line: str, target: str, left_delimeter: list, right_delimeter: list, return_captured: bool = False, limit=None, ranges=[0, -1]):
        return vey.special_split(line, target, left_delimeter, right_delimeter, return_captured, limit, ranges)
    
    @classmethod
    def special_find(cls, vey, line, target, left_delimeter, right_delimeter, ranges=[0, -1]):
        return vey.special_find(line, target, left_delimeter, right_delimeter, ranges)
    
    # 1.0.1
    @classmethod
    def delete(cls, vey, types: str, key = None, optional = None):
        allowed = ["variables", "functions", "classes", "library", "imports", "objects", "attributes"]
        if types in allowed:
            if types == "variables":
                del vey.variables[key]
                del vey.global_var[key]
                del vey.variable_info[key]
            elif types == "functions":
                if key in vey.functions.keys():
                    del vey.functions[key]
                else:
                    del vey.func_scope[key][optional]
            elif types == "classes":
                del vey.classes[key]
            elif types == "library":
                del vey.libraries[key]
                if key in vey.nplibs:
                    del vey.nplibs[key]
                    del vey.nplibs_acc[key]
            elif types == "imports":
                del vey.library[key]
                del vey.library_name[key]
                del vey.name_library[key]
            elif types == "objects":
                del vey.objects[key]
                del vey.class_callers[key]
            elif types == "attributes":
                del vey.objects[key]["variables"][optional]
        return vey

class external:
    """
    This class method gives Veyl access to python, or programs depending on the user's inputs
    this includes functions, classes, objects, variables, and even library objects.
    
    initiate by doing
        - init(veyl_object)
        
    these available tools and functions are
        - bind_function(name: str, function_object: object)
        - bind_class(name: str, class_object)
        - bind_object(name: str, object_name: object)
        - assign_variable(name: str, variable_value)
        - inject_library(name: str, library_object)
   
    external can also be used for special and simple configurations and changes during making
    an VEY instance for Veyl execution, tools such as
        - set_config(name, value)
        - remove_config(name: str)
        - get_config(name: str)
        - config_default()
        - config_save(filename: str, [path=Path.cwd()])
        - config_load(path: str)
        - return_config()
    """
    _original_config = {
        # Veyl objects
        "variables": {},
        "functions": {},
        "classes": {},
        "objects": {},
        "libraries": {},
        
        # System
        "filename": "-temp_veyl_executor-",
        "fileextension": ".vey",
        "path": Path.cwd(),
        
        # External injections
        "external": {}, # reserve keyword
        "injections": {
            "functions": {}, # python function, either user defined or built in
            "classes": {}, # python class
            "object": {}, # python object
            "libraries": {} # python library instance
        }
    }
    _config = _original_config.copy()
    vey = None
    @classmethod
    def init(cls, veyl_object: object):
        if not isinstance(veyl_object, VEY):
            raise TypeError("given object is not an instance of VEY")
        cls.vey = veyl_object
        # keep the live VEY instance in sync with whatever has been
        # configured on this class so far
        resolve_external.resolve(cls.vey, cls._config).start()

    @classmethod
    def bind_function(cls, name: str, function_object: object):
        cls._config["injections"]["functions"][name] = function_object
        if cls.vey is not None:
            resolve_external.resolve(cls.vey, cls._config).start()

    @classmethod
    def bind_classes(cls, name: str, class_object: object):
        cls._config["injections"]["classes"][name] = class_object
        if cls.vey is not None:
            resolve_external.resolve(cls.vey, cls._config).start()

    @classmethod
    def bind_object(cls, name: str, object_name: object):
        cls._config["injections"]["object"][name] = object_name
        if cls.vey is not None:
            resolve_external.resolve(cls.vey, cls._config).start()

    @classmethod
    def bind_library(cls, name: str, library: object):
        cls._config["injections"]["libraries"][name] = library
        if cls.vey is not None:
            resolve_external.resolve(cls.vey, cls._config).start()

    @classmethod
    def assign_variable(cls, name: str, value):
        cls.vey.assign_variable(f"{name} = {str(value)}", isexternal=True)

    @classmethod
    def inject_library(cls, name: str, library: object):
        cls.vey.nplibs[name] = library
        cls.vey.libraries.append(name)
        cls.vey.nplibs_acc[name] = False

    #configs
    @classmethod
    def set_config(cls, name: str, value):
        if name not in cls._config.keys():
            raise KeyError(f"given name `{name}` is not in the config variable")
        cls._config[name] = value
        if cls.vey is not None:
            resolve_external.resolve(cls.vey, cls._config).start()

    @classmethod
    def reset_config(cls, name: str):
        if name not in cls._config.keys():
            raise KeyError(f"given name `{name}` is not in the config variable")
        cls._config[name] = cls._original_config[name]
        if cls.vey is not None:
            resolve_external.resolve(cls.vey, cls._config).start()

    @classmethod
    def get_config(cls, name: str):
        if name not in cls._config.keys():
            raise KeyError(f"given name `{name}` is not in the config variable")
        return cls._config[name]

    @classmethod
    def config_default(cls):
        cls._config = cls._original_config.copy()
        if cls.vey is not None:
            resolve_external.resolve(cls.vey, cls._config).start()

    @classmethod
    def config_save(cls, file_name: str, path=None):
        # saves as a .vcon file
        path = Path.cwd() if path is None else path
        if isinstance(path, str):
            path = Path(path)
        if not path.is_dir():
            raise NotADirectoryError(f"invalid given directory {str(path)}")
        with open(path / Path(file_name).with_suffix(".vcon"), "w") as file:
            json.dump(cls._serializable_config(cls._config), file)

    @classmethod
    def config_load(cls, path: str):
        if not str(path).endswith(".vcon"):
            raise ValueError("expected a .vcon json file, but none is found")
        path = Path(path)
        if not path.is_file():
            raise FileNotFoundError("given file path does not exist")
        with open(path, "r") as file:
            loaded = json.load(file)
        cls._config.update(loaded)
        if cls.vey is not None:
            resolve_external.resolve(cls.vey, cls._config).start()
        return loaded
    
    @classmethod
    def return_config(cls):
        return cls._config
        
    @classmethod
    def _serializable_config(cls, config: dict):
        # injections hold live python objects/callables (functions, classes,
        # objects, libraries) which are not JSON serializable, so only the
        # plain data portion of the config is persisted to a .vcon file
        return {k: v for k, v in config.items() if k != "injections"}
    # 1.0.1
    @classmethod
    def run_state(cls, vey, program):
        if not isinstance(veyl_object, VEY):
            raise TypeError("given object is not an instance of VEY")
        vey.Instructions = vey.build_instructions(peogram)
        vey.full_instructions = vey.Instructions
        vey.raw_instructions = program
        vey.cnt, vey.og_c = 0, 0
        vey.execute()
        return vey
    
    @classmethod
    def save_obj(cls, vey, name: str):
        with open(name, "w") as file:
            json.dump(name, {vey: vey})
    
    @classmethod
    def load_obj(cls, name: str):
        return load_file(name)
    
    @classmethod
    def restart_run(cls, vey):
        inst = vey.raw_instructions
        module = vey.nplibs
        config = vey.external_config
        cr = vey.cause_raise
        io = vey.system_io
        path = vey.path
        file_name = vey.file_name
        file_extension = vey.file_extension
        program_version = vey.program_version
        isexternal = vey.is_external
        cli_config = vey._cli_config
        del vey
        vey = VEY(inst, module, cr, path, file_name, file_extension, config, isexternal, io, cli_config)
        vey.execute()
        return vey
    @classmethod
    def verbose(cls, program, isfile=False):
        code = program if not isfile else load_file(program)
        cli_config = {
            "verbose": True,
            "debug": False,
            "test": False
        }
        vey = VEY(code, cli_config=cli_config)
        vey.execute()
    
    @classmethod
    def debug(cls, program, isfile=False):
        code = program if not isfile else load_file(program)
        cli_config = {
            "verbose": False,
            "debug": True,
            "test": False
        }
        vey = VEY(code, cli_config=cli_config)
        vey.execute()
    
    @classmethod
    def check(cls, program, isfile=False):
        code = program if not isfile else load_file(program)
        cli_config = {
            "verbose": False,
            "debug": False,
            "test": True
        }
        vey = VEY(code, cli_config=cli_config)
        vey.execute()

class GetFunction:
    def __init__(self, vey, name):
        if not isinstance(vey, VEY):
            raise TypeError("given object is not a VEY type object (requires {type(VEY)} type)")
        elif not name in vey.functions.keys():
            raise NameError("given function name is not defined")
        self.name = name
        self.vey = vey
        self.function = vey.functions[name]
    
    def __call__(self, *args):
        arguments = [self.vey.convert_arg(arg, True) for arg in args]
        self.vey.run_functions(self.name, arguments, False)
        if self.vey.is_return:
            self.vey.is_return = False
            if len(self.vey.return_val) > 1:
                return tuple([a for a in self.vey.return_val])
            return self.vey.return_val[0]
        
class GetClass:  
    def __init__(self, vey, name):  
        if not isinstance(vey, VEY):  
            raise TypeError("given object is not a VEY type object (requires {type(VEY)} type)")  
        elif not name in vey.classes.keys():  
            raise NameError("given class name is not defined")  
        self._name = name  
        self._program = vey  
        self._cls_obj = vey.classes[name]
      
    def _call(self, name: str, *args):  
          
        args = [self._program.convert_arg(arg, True) for arg in args]  
  
        if name not in self._program.classes[self._name]["methods"].keys():  
            raise NameError("given name is not a defined method for class `{self._name}`")  
        t = False if self._program.classes[self._name]["methods"][name]["type"] == "pub" else True  
        self._program.run_methods(self._name, name, True, "<<external>>", args, t)  
        if self._program.is_return:  
            self._program.is_return = False  
            if len(self._program.return_val) > 1:  
                return tuple([a for a in self._program.return_val])  
            return self._program.return_val[0]  
              
    def __getattr__(self, name: str, *args):  
        internal_attr = {
            "_name": self._name
          , "_program": self._program
          , "_cls_obj": self._cls_obj
        }
        if name in internal_attr.keys():
            return internal_attr[name]
        if name in self._program.objects["<<external>>"]["variables"]["<dict>"]:
            return self._program.objects["<<external>>"]["variables"][name]
        return lambda *args: self._call(name, *args)  
      
    def __call__(self, *args):  
        args = str(tuple(args)) if len(args) > 0 else "()"  
        code = f"<<external>> = {self._name}{args}"  
        self._program.assign_variable(code, isexternal=True)  
        return self  
      
    def __hasattr__(self, name):  
        if name in self._program.objects[self._name]["variables"]["<attr>"]:  
            return True  
        return False
    
    def __setattr__(self, name, value):
        if name in ("_program", "_name", "_cls_obj"):
            object.__setattr__(self, name, value)
            return
    
        if name not in self._program.objects["<<external>>"]["variables"]:
            raise AttributeError(
                f"`{name}` is not a valid attribute"
            )
    
        self._program.objects["<<external>>"]["variables"][name] = value

class IncludeMeta(type):
    def __call__(cls, func):
        cls.data[func.__name__] = func
        return func
class include(metaclass=IncludeMeta):
    data = {}

    @classmethod
    def reset(cls):
        cls.data.clear()

    @classmethod
    def remove(cls, name):
        del cls.data[name]

if __name__ == "__main__":
    code = r"""
import time
rename time as t

/< Prints from 1 to N
number = input("enter maximum range > ").as(int)

start = t.time()

for cnt in range(1, number)
{
    output(cnt)
}

end = t.time()
est = end - start

output(f("Estimated taken time {est}"))
    """
    
    internal.execute(code)