import kagglehub

# Download latest version
path = kagglehub.model_download("sayannath235/american-sign-language/tfLite/american-sign-language")

print("Path to model files:", path)