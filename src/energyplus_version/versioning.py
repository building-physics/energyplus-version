# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause

class EnergyPlusVersion:
    def __init__(self, year, release, patch):
        self.year = year
        self.release = release
        self.patch = patch

    def next(self):
        year = self.year
        release = self.release + 1
        if release > 2:
            year += 1
            release = 1
        return EnergyPlusVersion(year, release, 0)

    def previous(self):
        year = self.year
        release = self.release - 1
        if release < 1:
            year -= 1
            release = 2
        return EnergyPlusVersion(year, release, 0)

    def __str__(self):
        return '%d.%d.%d' % (self.year, self.release, self.patch)

    def energyplus_identifier(self):
        return '%d.%d' % (self.year, self.release)

    @classmethod
    def from_string(cls, string):
        try:
            split = [int(el) for el in string.split('.')]
        except ValueError:
            return None
        if len(split) == 3:
            return cls(split[0], split[1], patch=split[2])
        return None

    @classmethod
    def from_energyplus_identifier(cls, string):
        try:
            split = [int(el) for el in string.split('.')]
        except ValueError:
            return None
        if len(split) == 2:
            return cls(split[0], split[1], patch=0)
        if len(split) == 3:
            return cls(split[0], split[1], patch=split[2])
        return None
