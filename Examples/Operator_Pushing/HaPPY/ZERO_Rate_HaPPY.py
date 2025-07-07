from OperatorPush.PushingToolbox import batch_push
from OperatorPush.Presets.HaPPY import setup_zero_rate_happy

tensor_list = setup_zero_rate_happy(R=2)

batch_push(tensor_list)
