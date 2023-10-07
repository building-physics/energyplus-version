# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
import jsonpatch

class Change:
    def apply(self) -> list:
        raise NotImplementedError('Change object must implement the "apply" method')
    def valid(self, object) -> bool:
        return False
    def describe(self) -> str:
        raise NotImplementedError('Change object must implement the "describe" method')

class ChangeFieldName:
    def __init__(self, object: str, old_name: str, new_name: str):
        self.object = object
        self.old_name = old_name
        self.new_name = new_name
    def apply(self) -> list:
        object_path = '/' + self.object + '/'
        from_path = object_path + self.old_name
        to_path = object_path + self.new_name
        #return [jsonpatch.MoveOperation({'op': 'move', 'from': from_path, 'path': to_path})]
        return [{'op': 'move', 'from': from_path, 'path': to_path}]
    def valid(self, object) -> bool:
        return self.old_name in object
    def describe(self) -> str:
        return 'Change the field named "%s" to "%s".' % (self.old_name, self.new_name)
    
class RemoveField:
    def __init__(self, object: str, field: str):
        self.object = object
        self.field = field
    def apply(self) -> list:
        path = '/' + self.object + '/' + self.field
        #return [jsonpatch.MoveOperation({'op': 'remove', 'path': path})]
        return [{'op': 'remove', 'path': path}]
    def valid(self, object) -> bool:
        return self.field in object
    def describe(self) -> str:
        return 'Remove the field "%s".' % self.field

class Upgrade:
    def __init__(self):
        self.changes = []
    def generate_patch(self, prev):
        patch = []
        for change in self.changes:
            if change.object in prev:
                for obj in prev[change.object]:
                    if change.valid(obj):
                        patch.append(change.apply('/' + change.object))
        return patch
    def describe(self):
        change_by_object = {}
        for change in self.changes:
            if change.object in change_by_object:
                change_by_object[change.object].append(change.describe())
            else:
                change_by_object[change.object] = [change.describe()]
        string =''
        for obj, changes in change_by_object.items():
            string += '# ' + obj + '\n'
            string += '\n\n'.join(changes) + '\n\n'
        return string
