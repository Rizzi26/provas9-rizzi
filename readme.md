# Súmario 

- [Prova da semana 09](#Prova-da-semana-09)
- [Configuração do ambiente virtual para rodar a atividade:](#configuração-do-ambiente-virtual-para-rodar-a-atividade)
- [Rodando meu servidor em seu computador:](#rodando-meu-servidor-em-seu-computador)
- [Explicação do código e suas principais funções dentro do servidor (arquivo main.py):](#explicação-do-código-e-suas-principais-funções-dentro-do-servidor-arquivo-mainpy)
- [Perguntas técnicas](#perguntas-técnicas)
    - [2.1. Descreva de maneira concisa (um parágrafo no máximo) o funcionamento do método de detecção escolhido.](#21-descreva-de-maneira-concisa-um-parágrafo-no-máximo-o-funcionamento-do-método-de-detecção-escolhido)
    - [2.2. Considere as seguintes alternativas para resolver o problema de detecção de faces:](#22-considere-as-seguintes-alternativas-para-resolver-o-problema-de-detecção-de-faces)
    - [2.3. Considerando as mesmas alternativas acima, faça uma nova classificação considerando a viabilidade técnica para detecção de emoções através da imagem de uma face.](#23-considerando-as-mesmas-alternativas-acima-faça-uma-nova-classificação-considerando-a-viabilidade-técnica-para-detecção-de-emoções-através-da-imagem-de-uma-face)
    - [2.4. A solução apresentada ou qualquer outra das que foram listadas na questão 2.2. tem a capacidade de considerar variações de um frame para outro (e.g. perceber que em um frame a pessoa está feliz e isso influenciar na detecção do próximo frame)? Se não, quais alterações poderiam ser feitas para que isso seja possível?](#24-a-solução-apresentada-ou-qualquer-outra-das-que-foram-listadas-na-questão-22-tem-a-capacidade-de-considerar-variações-de-um-frame-para-outro-eg-perceber-que-em-um-frame-a-pessoa-está-feliz-e-isso-influenciar-na-detecção-do-próximo-frame-se-não-quais-alterações-poderiam-ser-feitas-para-que-isso-seja-possível)
    - [2.5. (BONUS - não vale nada) Quem ganha a bola de ouro 2024?](#25-bonus---não-vale-nada-quem-ganha-a-bola-de-ouro-2024)
- [Vídeo para comprovar o funcionamento da atividade:](#vídeo-para-comprovar-o-funcionamento-da-atividade)
# Prova da semana 09

&emsp;Objetivo: Conseguir identificar rostos e minimizar falsos positivos no vídeo que foi disponibilizado para a prova, la_cabra.mp4.

# Configuração do ambiente virtual para rodar a atividade:

&emsp;Primeiro você deve clonar em sua máquina meu repositório, escolha uma pasta como por exemplo `Documents` e navegue até ela no terminal, em seguida digite `git clone https://github.com/Rizzi26/provas9-rizzi`.

&emsp;Agora com o repositório clonado ative a o ambiente virtual do python em sua máquina `venv`, digite o seguinte comando `python3 -m venv venv` e ative o ambiente virtual logo em seguida com o comando `source ./venv/bin/activate`

&emsp;E por fim, instale as dependências necessárias que utilizei nas importações com o comando `python3 -m pip install -r requirements.txt`

# Rodando meu servidor em seu computador:

&emsp;Agora com a venv ativada em sua máquina, navegue até o diretório `.../provas9-rizzi/src` e rode o seguinte comando para levantar o servidor `python3 main.py`

# Explicação do código e suas principais funções dentro do servidor (arquivo main.py):

&emsp;Aqui podemos observar as libys necessárias para o funcionamento do projeto.

- Flask --> Nosso servidor.
- cv2 --> Nos ajuda a manipular a parte da visão computacional e lidar com os frames para o reconhecimento facial.
- tempfile --> Manipulação de arquivos temporários.

```python
from flask import Flask, request, render_template
import cv2
import tempfile
```

&emsp;Este trecho de código configura o servidor web Flask e cria a nossa primeira rota index, que servirá um arquivo html para inputar vídeos que irão ser tratados pelo backend para o reconhecimento facial:

```python
app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def index():
    return render_template('index.html')
```

&emsp;Aqui podemos ver o arquivo html que aparece para o cliente inserir o seu vídeo para o reconhecimento de faces:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visão Computacional</title>
</head>
<body>
    <div class="main">
        <div class="container">
            <div class="titleprin">
                <h2>Aplicação prática de Redes Convolucionais</h2>
            </div>
            <div class="container2">
                <div>
                    <input type="file" id="inputVideo" />
                    <button onclick="sendVideo()">Enviar vídeo</button>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
```

&emsp;Ao clicar no botão para fazer o envio do vídeo e chamar a função `sendVideo()` podemos ver a lógica por traz nesse arquivo JS que tem uma requisição fetch para nosso backend enviando um formdata:

```JavaScript
        function sendVideo() {
            const input = document.getElementById('inputVideo');
            const file = input.files[0];

            if (file) {
                const formData = new FormData();
                formData.append('video', file);

                fetch('/input', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok.');
                    }
                    return response.blob();
                })

                .catch(error => console.error('Error:', error));
            } else {
                alert('Por favor, selecione um arquivo de vídeo primeiro.');
            }
        }
```

&emsp;Quando o vídeo chega ao backend ele é recebido pela rota `/input` e armazenado em bytes, nessa mesma rota chamamos a função `identify_faces(video_bytes)`:

```python
@app.route('/input', methods=['POST'])
def input():
    if 'video' not in request.files:
        return "No video file", 400
    
    video_file = request.files['video']
    video_bytes = video_file.read()

    identify_faces(video_bytes)

    return "processando", 200
```

&emsp;Na função `identify_faces()` carregamos dois classificadores `haarcascade` um para identificar frontalmente a face de um ser humano e outro para identifcar quando um rosto fica de lado, assim conseguimos ter um melhor resultado quando o vídeo for tratado.

```python
def identify_faces(data):
    classifier_frontal = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    classifier_profile = cv2.CascadeClassifier('haarcascade_profileface.xml')

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        temp_video.write(data)
        temp_video_path = temp_video.name

    video_capture = cv2.VideoCapture(temp_video_path)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    output_path = 'output.mp4'
    out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(video_capture.get(3)), int(video_capture.get(4))))

    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces_frontal = classifier_frontal.detectMultiScale(gray, 1.3, 5)
        faces_profile = classifier_profile.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces_frontal:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        for (x, y, w, h) in faces_profile:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        out.write(frame)

    video_capture.release()
    out.release()

    return output_path
```

&emsp;No codigo acima podemos descrver importantes partes, como:

- Carregar os classificadores para identificar faces.
- A criação de um arquivo temporário para escrever os bytes nesse arquivo.
- Deixa pronto como será a saída desse novo arquivo, que terá o nome de `output.mp4`.
- Looping que recebe esses frames, converte para uma escala de cinza, reconhece os padrões de maneira frontal e de perfil e em cima do frame original desenha um retangulo onde são identificados os rostos.

# Perguntas técnicas:

## 2.1. Descreva de maneira concisa (um parágrafo no máximo) o funcionamento do método de detecção escolhido.

&emsp;O método de detecção de faces utilizado baseia-se em classificadores Haar Cascades, uma técnica do OpenCV amplamente utilizada para reconhecimento facial. Os Haar Cascades são essencialmente filtros baseados em características visuais aprendidas, como bordas, linhas e padrões de textura que são comuns em faces humanas. O processo começa convertendo o frame de vídeo para escala de cinza para simplificar o processamento. Em seguida, cada classificador Haar Cascade é aplicado ao frame para detectar padrões correspondentes a rostos frontais e de perfil. Quando um padrão é encontrado, um retângulo é desenhado em torno da área detectada. Este método é eficiente para detecção em tempo real, embora possa exigir ajustes nos parâmetros de escala e detecção dependendo das condições de iluminação e orientação dos rostos.

## 2.2. Considere as seguintes alternativas para resolver o problema de detecção de faces:

&emsp;CNN:

- Viabilidade técnica: Alta. CNNs são altamente eficazes em reconhecimento facial devido à capacidade de aprender características complexas e hierárquicas das imagens.
- Facilidade de implementação: Moderada. Implementar uma CNN pode ser complexo devido ao treinamento exigido.
- Versatilidade da solução: Média. CNNs podem ser treinadas para uma variedade de tarefas além da detecção de faces.

&emsp;HAAR Cascade:

- Viabilidade técnica: Moderada. HAAR Cascades são eficientes para detecção de faces, mas podem ser limitados quando as faces com orientações não estão no padrão.
- Facilidade de implementação: Alta. Implementar um detector de face com HAAR Cascade é simples e eficiente para aplicações básicas.
- Versatilidade da solução: Moderada. É menos flexível em termos de adaptação a novos cenários e tarefas além da detecção de faces.

&emsp;NN Linear:

- Viabilidade técnica: Baixa. Redes Neurais Lineares não são adequadas para problemas complexos de visão computacional como detecção de faces.
- Facilidade de implementação: Alta. São simples de implementar, mas sua aplicação é limitada em tarefas que exigem capacidades complexas.
- Versatilidade da solução: Baixa. São limitadas em sua capacidade de generalização.

&emsp;Filtros de correlação cruzada

- Viabilidade técnica: Dependen da aplicação específica, filtros de correlação cruzada podem ser usados para tarefas como detecção de bordas e características básicas.
- Facilidade de implementação: Moderada. Implementar filtros de correlação cruzada pode ser direto, mas sua eficácia depende muito da escolha dos filtros e da aplicação específica.
- Versatilidade da solução: Baixa. São mais adequados para tarefas de processamento de imagem específicas e menos para reconhecimento de objetos complexos como faces.

## 2.3. Considerando as mesmas alternativas acima, faça uma nova classificação considerando a viabilidade técnica para detecção de emoções através da imagem de uma face.

- CNN (Redes Neurais Convolucionais): Alta. CNNs são altamente adequadas para detectar e interpretar padrões complexos em imagens.
- HAAR Cascade: Baixa. HAAR Cascades são menos eficazes na detecção de emoções específicas.
- NN Linear (Redes Neurais Lineares): Baixa. Redes Neurais Lineares não possuem a capacidade de capturar as características complexas necessárias para identificar emoções através de expressões faciais.
- Filtros de correlação cruzada: Baixa. Estão focados em características estruturais simples.

## 2.4. A solução apresentada ou qualquer outra das que foram listadas na questão 2.2. tem a capacidade de considerar variações de um frame para outro (e.g. perceber que em um frame a pessoa está feliz e isso influenciar na detecção do próximo frame)? Se não, quais alterações poderiam ser feitas para que isso seja possível?

&emsp;A solução baseada em HAAR Cascades, por si só, não possui a capacidade de considerar variações entre frames para interpretar estados emocionais contínuos. Para habilitar essa funcionalidade, seriam necessárias abordagens mais avançadas, como o uso de modelos de Deep Learning (como CNNs) treinados para reconhecer emoções ao longo do tempo, utilizando técnicas de sequenciamento ou redes recorrentes para capturar mudanças de estado.

# 2.5. (BONUS - não vale nada) Quem ganha a bola de ouro 2024?

- Foi o Pelé.

# Vídeo para comprovar o funcionamento da atividade:

&emsp;Podemos observar que ao ligar o servidor, enviar o vídeo e receber a saída (output.mp4) não demorou muito, pois utilizamos um dataset leve para identificar as faces. **Clique no template abaixo** para ser redirecionado para o **YouTube e reproduzir o vídeo**:

[![Vídeo que comprova plenamente o funcionamento do sistema criado](https://midias.correiobraziliense.com.br/_midias/jpg/2021/11/29/675x450/1_whatsapp_image_2021_11_29_at_18_29_16-7134341.jpeg?20221017095143?20221017095143)](https://youtu.be/14FcOx9Z-m8)