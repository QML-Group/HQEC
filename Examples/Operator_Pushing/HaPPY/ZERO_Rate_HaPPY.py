from LEGO_HQEC.OperatorPush.PushingToolbox import batch_push
from LEGO_HQEC.OperatorPush.Presets.HaPPY_code import setup_zero_rate_happy

tensor_list = setup_zero_rate_happy(R=2)

batch_push(tensor_list)
