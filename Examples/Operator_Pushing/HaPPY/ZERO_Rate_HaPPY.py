from OperatorPush.PushingToolbox import batch_push
from OperatorPush.Presets.Zero_Rate_HaPPY_new_for_kj import setup_zero_rate_happy

tensor_list = setup_zero_rate_happy(R=2)

batch_push(tensor_list)
