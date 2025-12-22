import torch
print('exe:', __import__('sys').executable)
print('torch:', torch.__version__)
print('cuda_available:', torch.cuda.is_available())
print('device_count:', torch.cuda.device_count())
if torch.cuda.is_available():
    print('device_name:', torch.cuda.get_device_name(0))
