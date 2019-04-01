import os
import pickle
from functools import wraps


class SaveLoadDescriptor:
    """
    Descriptor class which supports saving automatically to avoid
    recomputing expensive computations.
    """

    __slots__ = ("name", "value", "directory")

    def __init__(self, name):
        self.name = name

        # Different classes might have attributes of the same name,
        # so we need to map the class to the actual value
        self.value = dict()

    def get_file_name(self, instance):
        return "{}.{}.pickle".format(instance.__name__, self.name)

    def __set__(self, instance, value):
        file_name = self.get_file_name(instance)

        # Create the folder to save the temporary files
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        with open("{}/{}".format(self.directory, file_name), "wb") as f:
            pickle.dump(value, f)

        self.value[instance] = value

    def __get__(self, instance, owner):
        if self.name not in instance.__slots__:
            raise AttributeError(
                "{} has no attribute {}".format(instance.__name__, self.name)
            )

        value = self.value.get(instance, None)
        if value is not None:
            # The value exists, which means either this value was loaded from files,
            # or computed in a previous function, we just need return this value
            return value

        file_name = self.get_file_name(instance)

        try:
            with open("{}/{}".format(self.directory, file_name), "rb") as f:
                print("\nLoading precomputed {} from file".format(file_name[:-7]))
                value = pickle.load(f)

            self.value[instance] = value
            return value
        except FileNotFoundError:
            # This is the first time getting the attribute, return None to execute
            # the function computing this attribute, using the `load_attr` decorator
            return None


class LogAttribute(type):
    def __new__(mcs, name, bases, namespace):
        # Create and assign decriptors based on __slots__ of the derived classes
        for key in namespace["__slots__"]:
            # Skip names containing df since they are DataFrames loaded from the GTFS files,
            # also skip attributes which are already assigned
            if "df" not in key and key not in mcs.__dict__:
                setattr(mcs, key, SaveLoadDescriptor(key))

        return super().__new__(mcs, name, bases, namespace)


def load_attr(*attr_names):
    """
    Return the decorator to check if the attributes was already computed.
    If not, compute and set the attribute using the decorated (class)method.

    attr_names can be the strings representing the name of the attributes
    in the current class; or it can be a single dict, this dict maps the classes
    to the attributes which are to be computed by the decorated class method.

    In the latter case, to add the attributes name from the current class,
    the key should be None.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(cls, *args, **kwargs):
            if len(attr_names) == 1 and isinstance(attr_names[0], dict):
                val = True
                for cls_, names in attr_names[0].items():
                    if val is None:
                        break

                    # Map the key None to the current class
                    if cls_ is None:
                        cls_ = cls

                    if isinstance(names, str):
                        names = [names]

                    val = val and (
                        all(getattr(cls_, name) is not None for name in names) or None
                    )
            else:
                val = all(getattr(cls, name) is not None for name in attr_names) or None

            if val is None:
                func(cls, *args, **kwargs)

        return wrapper

    return decorator
