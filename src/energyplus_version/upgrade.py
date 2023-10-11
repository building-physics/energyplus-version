# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause

class Change:
    def apply(self, object_name) -> list: # pragma: no cover
        raise NotImplementedError('Change object must implement the "apply" method')
    def valid(self, object) -> bool: # pragma: no cover
        raise NotImplementedError('Change object must implement the "apply" method') 
    def describe(self) -> str: # pragma: no cover
        raise NotImplementedError('Change object must implement the "describe" method')

class ChangeFieldName:
    def __init__(self, object: str, old_name: str, new_name: str):
        self.object = object
        self.old_name = old_name
        self.new_name = new_name
    def apply(self, object_name) -> list:
        object_path = '/%s/%s/' % (self.object, object_name)
        from_path = object_path + self.old_name
        to_path = object_path + self.new_name
        return [{'op': 'move', 'from': from_path, 'path': to_path}]
    def valid(self, object) -> bool:
        return self.old_name in object
    def describe(self) -> str:
        return 'Change the field named "%s" to "%s".' % (self.old_name, self.new_name)
    
class RemoveField:
    def __init__(self, object: str, field: str):
        self.object = object
        self.field = field
    def apply(self, object_name) -> list:
        path = '/%s/%s/%s' % (self.object, object_name, self.field)
        return [{'op': 'remove', 'path': path}]
    def valid(self, object) -> bool:
        return self.field in object
    def describe(self) -> str:
        return 'Remove the field named "%s".' % self.field

class Upgrade:
    def changes(self): # pragma: no cover
        raise NotImplementedError('Upgrade object must implement the "changes" method')
    def generate_patch(self, prev):
        patch = []
        for change in self.changes():
            if change.object in prev:
                for name, obj in prev[change.object].items():
                    if change.valid(obj):
                        patch.extend(change.apply(name))
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
        if patch != []:
            path = '/Version/%s/version_identifier' % list(prev['Version'].keys())[0]
            patch.append({'op': 'replace', 'path': path, 'value': self.to_version()})
        return patch
        