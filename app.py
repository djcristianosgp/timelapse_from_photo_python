from pathlib import Path
from datetime import datetime
import cv2
import requests
import shutil
from moviepy.editor import VideoFileClip, AudioFileClip

def buscar_imagens_do_dia(pasta):
    hoje = datetime.now().date()
    imagens = sorted([
        str(f) for f in Path(pasta).glob("*.jpg")
        if datetime.fromtimestamp(f.stat().st_mtime).date() == hoje
    ])
    return imagens

def adicionar_logo(frame, logo_path, posicao):
    logo = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    logo = cv2.resize(logo, (100, 100))
    lh, lw = logo.shape[:2]
    fh, fw = frame.shape[:2]

    x, y = {
        'esquerda': (10, 10),
        'direita': (fw - lw - 10, 10)
    }[posicao]

    roi = frame[y:y+lh, x:x+lw]
    mask = logo[:, :, 3] if logo.shape[2] == 4 else None
    if mask is not None:
        for c in range(3):
            roi[:, :, c] = roi[:, :, c] * (1 - mask/255) + logo[:, :, c] * (mask/255)
    else:
        roi[:] = logo

    frame[y:y+lh, x:x+lw] = roi
    return frame

def adicionar_texto(frame):
    font = cv2.FONT_HERSHEY_SIMPLEX
    texto = "Patrocine aqui"
    tamanho = 1
    espessura = 2
    cor = (255, 255, 255)
    pos = (frame.shape[1]//2 - 150, frame.shape[0] - 20)
    cv2.putText(frame, texto, pos, font, tamanho, cor, espessura, cv2.LINE_AA)
    return frame

def criar_timelapse(imagens, output_path, logo_esq, logo_dir):
    frame_size = (1920, 1080)
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), 30, frame_size)

    for imagem in imagens:
        frame = cv2.imread(imagem)
        frame = cv2.resize(frame, frame_size)

        frame = adicionar_logo(frame, logo_esq, 'esquerda')
        frame = adicionar_logo(frame, logo_dir, 'direita')
        frame = adicionar_texto(frame)

        out.write(frame)

    out.release()

def adicionar_audio_ao_video(video_path, audio_path, output_path):
    video = VideoFileClip(video_path)
    audio = AudioFileClip(audio_path).subclip(0, video.duration).audio_fadeout(1)
    video = video.set_audio(audio)
    video.write_videofile(output_path, codec="libx264", audio_codec="aac")

def enviar_para_api(video_path, url):
    with open(video_path, 'rb') as f:
        response = requests.post(url, files={'file': f})
    return response.status_code

def mover_imagens(imagens, destino_base):
    for img in imagens:
        data = datetime.fromtimestamp(Path(img).stat().st_mtime)
        destino = Path(destino_base) / f"{data.year}/{data.month:02}/{data.day:02}"
        destino.mkdir(parents=True, exist_ok=True)
        shutil.move(img, destino / Path(img).name)

def main():
    pasta_imagens = "/caminho/imagens"
    destino_video_raw = "/tmp/timelapse_raw.mp4"
    trilha_audio = "/caminho/audio.mp3"
    destino_video_final = "/caminho/final/timelapse_com_audio.mp4"
    logo_esquerda = "/caminho/logo_esq.png"
    logo_direita = "/caminho/logo_dir.png"
    destino_arquivos = "/caminho/imagens_processadas"
    url_api = "https://suaapi.com/upload"

    imagens = buscar_imagens_do_dia(pasta_imagens)
    if not imagens:
        print("Nenhuma imagem do dia encontrada.")
        return

    criar_timelapse(imagens, destino_video_raw, logo_esquerda, logo_direita)
    adicionar_audio_ao_video(destino_video_raw, trilha_audio, destino_video_final)

    status = enviar_para_api(destino_video_final, url_api)
    print(f"Status do upload: {status}")

    mover_imagens(imagens, destino_arquivos)

if __name__ == "__main__":
    main()
