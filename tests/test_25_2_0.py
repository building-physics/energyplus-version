# SPDX-FileCopyrightText: 2023-present Oak Ridge National Laboratory, managed by UT-Battelle
#
# SPDX-License-Identifier: BSD-3-Clause
from copy import deepcopy

import jsonpatch


def apply_upgrade(model):
    from energyplus_version.version_25_2_0 import Upgrade

    return jsonpatch.JsonPatch(Upgrade().generate_patch(model)).apply(model)


def test_parallel_piu_removes_reheat_coil_air_inlet_node_name():
    model = {
        "AirTerminal:SingleDuct:ParallelPIU:Reheat": {
            "Parallel PIU": {
                "outlet_node_name": "Parallel PIU Outlet",
                "reheat_coil_air_inlet_node_name": "Parallel PIU Reheat Inlet",
                "zone_mixer_name": "Parallel PIU Mixer",
            }
        }
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded == {
        "AirTerminal:SingleDuct:ParallelPIU:Reheat": {
            "Parallel PIU": {
                "outlet_node_name": "Parallel PIU Outlet",
                "zone_mixer_name": "Parallel PIU Mixer",
            }
        }
    }


def test_series_piu_removes_reheat_coil_air_inlet_node_name():
    model = {
        "AirTerminal:SingleDuct:SeriesPIU:Reheat": {
            "Series PIU": {
                "outlet_node_name": "Series PIU Outlet",
                "reheat_coil_air_inlet_node_name": "Series PIU Reheat Inlet",
                "zone_mixer_name": "Series PIU Mixer",
            }
        }
    }
    original = deepcopy(model)

    upgraded = apply_upgrade(model)

    assert model == original
    assert upgraded == {
        "AirTerminal:SingleDuct:SeriesPIU:Reheat": {
            "Series PIU": {
                "outlet_node_name": "Series PIU Outlet",
                "zone_mixer_name": "Series PIU Mixer",
            }
        }
    }
