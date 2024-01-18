# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause

class UpgradeError(Exception):
    pass

class UpgradeWarning(Warning):
    pass

class Change:
    def apply_to_all(self, objects: dict) -> list: # pragma: no cover
        raise NotImplementedError('Change object must implement the "apply_to_all" method')
    def apply(self, object_name: str, object: dict) -> list: # pragma: no cover
        raise NotImplementedError('Change object must implement the "apply" method')
    def valid(self, object) -> bool: # pragma: no cover
        raise NotImplementedError('Change object must implement the "apply" method') 
    def describe(self) -> str: # pragma: no cover
        raise NotImplementedError('Change object must implement the "describe" method')

def do_nothing(input):
    return True

class ChangeFieldName(Change):
    def __init__(self, object: str, old_name: str, new_name: str):
        self.object = object
        self.old_name = old_name
        self.new_name = new_name
    def apply_to_all(self, objects: dict) -> list:
        patch = []
        for name, object in objects.items():
            if self.old_name in object:
                patch.extend(self.apply(name, object))
        return patch
    def apply(self, object_name: str, object: dict) -> list:
        object_path = '/%s/%s/' % (self.object, object_name)
        from_path = object_path + self.old_name
        to_path = object_path + self.new_name
        return [{'op': 'move', 'from': from_path, 'path': to_path}]
    def valid(self, object) -> bool:
        return self.old_name in object
    def describe(self) -> str:
        return 'Change the field named "%s" to "%s".' % (self.old_name, self.new_name)
    
class RemoveField(Change):
    def __init__(self, object: str, field: str, check_value=None):
        self.object = object
        self.field = field
        self.check_value = do_nothing
        if check_value is not None:
            if not callable(check_value):
                raise UpgradeError('RemoveField expected a callable for "check_value", instead got "%s"' % repr(check_value))
            self.check_value = check_value
    def apply(self, object_name: str, object: dict) -> list:
        path = '/%s/%s/%s' % (self.object, object_name, self.field)
        return [{'op': 'remove', 'path': path}]
    def apply_to_all(self, objects: dict) -> list:
        patch = []
        for name, object in objects.items():
            if self.field in object:
                if self.check_value(object[self.field]):
                    patch.extend(self.apply(name, object))
        return patch
    def valid(self, object) -> bool:
        if self.field in object:
            return self.check_value(object[self.field])
        return False
    def describe(self) -> str:
        return 'Remove the field named "%s".' % self.field

class MapValues(Change):
    def __init__(self, object: str, field: str, value_map: dict):
        self.object = object
        self.field = field
        self.value_map = value_map
    def apply_to_all(self, objects: dict) -> list:
        patch = []
        for name, object in objects.items():
            if self.field in object and object[self.field] in self.value_map:
                patch.extend(self.apply(name, object))
        return patch
    def apply(self, object_name: str, object: dict) -> list:
        path = '/%s/%s/%s' % (self.object, object_name, self.field)
        return [{'op': 'replace', 'path': path, 'value': self.value_map[object[self.field]]}]
    def valid(self, object) -> bool:
        if self.field in object:
            return object[self.field] in self.value_map
        return False
    def describe(self) -> str:
        return 'Change the values of field named "%s" as follows: %s.' % (self.field, ', '.join(['"%s" to "%s"' % (k, v) for k,v in self.value_map.items()]))

class ChangeObjectName(Change):
    def __init__(self, object: str, new_name: str):
        self.object = object
        self.new_name = new_name
    def apply_to_all(self, objects: dict) -> list:
        if not objects:
            return []
        from_path = '/%s' % self.object
        to_path = '/%s' % self.new_name
        return [{'op': 'move', 'from': from_path, 'path': to_path}]
    def apply(self, object_name: str, object: dict) -> list:
        from_path = '/%s' % self.object
        to_path = '/%s' % self.new_name
        return [{'op': 'move', 'from': from_path, 'path': to_path}]
    def valid(self, object) -> bool:
        return True
    def describe(self) -> str:
        return 'Change the name of the object named "%s" to "%s".' % (self.object, self.new_name)

class SplitObject(Change):
    def __init__(self, fields_by_object: dict):
        self.fields_by_object = fields_by_object

class Upgrade:
    def changes(self): # pragma: no cover
        raise NotImplementedError('Upgrade object must implement the "changes" method')
    def generate_patch(self, prev):
        patch = []
        for change in self.changes():
            objects = prev.get(change.object, {})
            patch.extend(change.apply_to_all(objects))
            #if change.object in prev:
            #    for name, obj in prev[change.object].items():
            #        if change.valid(obj):
            #            patch.extend(change.apply(name, obj))
        return patch
    def describe(self):
        change_by_object = {}
        for change in self.changes():
            if change.object in change_by_object:
                change_by_object[change.object].append(change.describe())
            else:
                change_by_object[change.object] = [change.describe()]
        string =''
        for obj, changes in change_by_object.items():
            string += '# Object Change: ' + obj + '\n'
            string += '\n\n'.join(changes) + '\n\n'
        return string

class EnergyPlusUpgrade(Upgrade):
    def from_version(self) -> str: # pragma: no cover
        raise NotImplementedError('EnergyPlusUpgrade object must implement the "from_version" method')
    def to_version(self) -> str: # pragma: no cover
        raise NotImplementedError('EnergyPlusUpgrade object must implement the "to_version" method')
    def generate_patch(self, prev):
        patch = super().generate_patch(prev)
        try:
            path = '/Version/%s/version_identifier' % list(prev['Version'].keys())[0]
            patch.append({'op': 'replace', 'path': path, 'value': self.to_version()})
        except KeyError:
            pass
        return patch
        