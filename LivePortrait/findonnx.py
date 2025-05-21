import os
import onnxruntime as ort

# Путь к папке с установленным onnxruntime
ort_path = os.path.dirname(ort.__file__)
providers_path = os.path.join(ort_path, 'capi')
print(f"Путь к провайдерам ONNX Runtime: {providers_path}")
print(f"Содержимое папки:")
for file in os.listdir(providers_path):
    print(f" - {file}")