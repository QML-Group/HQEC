from hqec.operator_push.push_toolbox import batch_push
from hqec.operator_push.presets.zero_rate_happy_new_for_kj import setup_zero_rate_happy

tensor_list = setup_zero_rate_happy(R=2)

batch_push(tensor_list)
