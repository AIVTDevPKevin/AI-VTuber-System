import torch










def torch_check_is_gpu_available():
    if torch.cuda.is_available():
        print(f"GPU is available: {torch.cuda.get_device_name(0)}")

    else:
        print("GPU is not available")










if __name__ == '__main__':
    torch_check_is_gpu_available()
    input("Press any key to continue")




