from osp.core.namespaces import mods
from typing import List
from osp.core.cuds import Cuds


class SimCaseTemplate:
    def __init__(
            self,
            template: str,
            inputs: List[Cuds],
            settings: List[Cuds],
            outputs: List[Cuds]
        ) -> None:

        self.caseInputTopEntity = mods.DataPoint
        self.caseSettingsTopEntity = mods.Settings
        self.template = template
        self.inputs = inputs
        self.settings = settings
        self.outputs = outputs


MOO = SimCaseTemplate(
    template="MOO",
    settings = [mods.SettingItem],
    inputs = [mods.DataPointItem],
    outputs = [mods.ParetoFront],
)
