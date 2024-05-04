import importlib
import functools
import sys

class ModuleLoader(object):
    _instance = None
    modules = {}
    __current_module = None
    hServ = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    @classmethod
    def action_load_module(cls, data):
        T_e = cls.load_module(data["module_name"])
        if T_e != "":
            return "Module " + data["module_name"] + " not loaded :" + T_e
        return "Module " + data["module_name"] + " loaded"
    @classmethod
    def action_delete_module(cls, data):
        module_name = data["module_name"]
        if module_name in cls.modules:
            if cls.modules[module_name]["stop"] is not None:
                cls.modules[module_name]["stop"](cls.modules[module_name]["module"])
            for action in cls.modules[module_name]["actions"]:
                cls.hServ.RemoveAction(action)
            del cls.modules[module_name]
            return "Module " + data["module_name"] + " deleted"
        return "No module " + data["module_name"]
    @classmethod
    def setServer(cls, server):
        if cls.hServ is not None:
            return
        cls.hServ = server
        cls.hServ.AddAction("ModuleLoad", lambda data: cls.action_load_module(data))
        cls.hServ.AddAction("ModuleDelete", lambda data: cls.action_delete_module(data))

    @classmethod
    def register(cls, name, func):
        if cls.__current_module is None:
            return
        if cls.__current_module not in cls.modules:
            cls.modules[cls.__current_module] = {"module": None, "start": None, "stop": None, "actions": {}}
        cls.modules[cls.__current_module]["actions"][name] = func
    @classmethod
    def register_class_data(cls, part, data):
        if cls.__current_module is None:
            return
        if cls.__current_module not in cls.modules:
            return
        cls.modules[cls.__current_module][part] = data
    @classmethod
    def load_module(cls, module_name):
        current_module_actions = None
        current_module_data = None
        if module_name in cls.modules:
            current_module_actions = cls.modules[module_name]
            if cls.modules[module_name]["stop"] is not None:
                current_module_data = cls.modules[module_name]["stop"](cls.modules[module_name]["module"])
            for action in cls.modules[module_name]["actions"]:
                cls.hServ.RemoveAction(action)
            del cls.modules[module_name]

        cls.__current_module = module_name
        error = ""
        try:
            if ("%s" % module_name) in sys.modules:
                importlib.reload(sys.modules["%s" % module_name])
            else:
                importlib.import_module("%s" % module_name)
        except Exception as e:
            error = str(e)
        cls.__current_module = None

        if ("%s" % module_name) in sys.modules:
            if error != "":
                cls.modules[module_name] = current_module_actions
            if cls.modules[module_name]["start"] is not None:
                cls.modules[module_name]["start"](cls.modules[module_name]["module"], current_module_data)
            for action in cls.modules[module_name]["actions"]:
                cls.hServ.AddAction(action,
                    lambda data, c_module_name=module_name, c_action=action:
                    cls.modules[c_module_name]["actions"][c_action](cls.modules[c_module_name]["module"], data)
                                    )
            return error
        return error



ModuleLoader()

def singleton(cls):
    print("sin")
    ModuleLoader.register_class_data("module", cls)
    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if wrapper_singleton.instance is None:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance

    wrapper_singleton.instance = None
    return wrapper_singleton

def action(name):
    print("action", name)
    def action_by_name(func):
        ModuleLoader.register(name, func)
        return func
    return action_by_name


def module_start(func):
    ModuleLoader.register_class_data("start", func)
    return func

def module_stop(func):
    ModuleLoader.register_class_data("stop", func)
    return func

