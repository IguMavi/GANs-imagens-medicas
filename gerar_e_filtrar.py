import os
import sys
import pickle
import torch
import numpy as np
import cv2
import PIL.Image

# Garante que o Python encontre os submódulos dnnlib e torch_utils do StyleGAN3
sys.path.insert(0, os.getcwd())
import dnnlib

# FORÇAR IMPLEMENTAÇÃO EM PYTHON (Evita o erro de compilação do bias_act_plugin)
from torch_utils.ops import bias_act
bias_act.plugin_options = {'use_custom_op': False}

def aplicar_nlmeans(imagem_pil, h=6, templateWindowSize=7, searchWindowSize=21):
    """
    Converte a imagem PIL para o formato do OpenCV, aplica o filtro 
    Non-Local Means para imagens coloridas e retorna uma imagem PIL.
    """
    img_cv = cv2.cvtColor(np.array(imagem_pil), cv2.COLOR_RGB2BGR)
    img_filtrada = cv2.fastNlMeansDenoisingColored(
        src=img_cv,
        dst=None,
        h=h,
        hColor=h,             
        templateWindowSize=templateWindowSize,
        searchWindowSize=searchWindowSize
    )
    return PIL.Image.fromarray(cv2.cvtColor(img_filtrada, cv2.COLOR_BGR2RGB))

def pipeline_automatizado(caminho_pkl, pasta_saida, total_imagens=3000, truncation_psi=0.7):
    os.makedirs(pasta_saida, exist_ok=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"[-] Usando dispositivo: {device}")
    
    print("[-] Carregando os pesos do StyleGAN3... (isso pode levar um momento)")
    with dnnlib.util.open_url(caminho_pkl) as f:
        G = pickle.load(f)['G_ema'].to(device)
    
    print(f"[-] Iniciando a geração de {total_imagens} imagens com filtro NLMeans...")
    
    for seed in range(1, total_imagens + 1):
        z = torch.from_numpy(np.random.RandomState(seed).randn(1, G.z_dim)).to(device)
        label = torch.zeros([1, G.c_dim]).to(device)
        
        with torch.no_grad():
            img_tensor = G(z, label, truncation_psi=truncation_psi)
        
        img_tensor = (img_tensor.permute(0, 2, 3, 1) * 127.5 + 128).clamp(0, 255).to(torch.uint8)
        img = img_tensor.squeeze(0).cpu().numpy()
        img_pil = PIL.Image.fromarray(img, 'RGB')
        
        img_filtrada = aplicar_nlmeans(img_pil, h=6) 
        
        caminho_final = os.path.join(pasta_saida, f'seed_{seed:04d}.png')
        img_filtrada.save(caminho_final)
        
        if seed % 50 == 0 or seed == total_imagens:
            print(f"[>] Progresso: {seed}/{total_imagens} imagens processadas.")

if __name__ == "__main__":
    # Garante que o ambiente ignore os plugins customizados em C++ se der erro
    os.environ['TORCH_EXTENSIONS_DIR'] = os.path.join(os.getcwd(), 'torch_extensions')
    
    CAMINHO_DO_SEU_PKL = "/home/igor/stylegan3/network-snapshot-000008.pkl"
    PASTA_DE_DESTINO = "/home/igor/stylegan3/data_fakes"
    
    pipeline_automatizado(
        caminho_pkl=CAMINHO_DO_SEU_PKL, 
        pasta_saida=PASTA_DE_DESTINO, 
        total_imagens=3000, 
        truncation_psi=0.7
    )
