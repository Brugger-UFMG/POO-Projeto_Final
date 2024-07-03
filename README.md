# POO-Projeto_Final
Este repositório contêm os arquivos referentes à entrega do Projeto Final da disciplina de Programação Orientada a Objetos.  
O projeto final é um jogo, desenvolvido em Python, que utiliza conceitos da programação orientada a objetos e modularização.

## Instruções
### Executando o jogo pela linha de comando:
O projeto pode ser executado utilizando o comando:  
`python -m scripts.main`  
O Comando deve ser executado no diretório superior ao diretório "scripts/".  
Nesse mesmo diretório onde o comando está sendo executado, também deve estar presente a pasta "graphics/".

### Executando o jogo utilizando o executável:
O jogo também pode ser facilmente executado utilizando o arquivo "Projeto Final POO.exe" disponibilizado.  
Note que o executável __não é portable__, portanto, na mesma pasta do executável deve estar presente pasta "graphics/".

## Sobre o Jogo
Um desenvolvedor com poucos conhecimentos de programação criou um programa cheio de _bugs_.  
Você controla um robozinho, que tenta tratar todos os _bugs_ deste programa em tempo de execução.

### Controles
* __W, A, S, D:__ Movimentação do jogador para cima, esquerda, baixo e direita, respectivamente.  
* __Barra de Espaço:__ Realiza uma esquiva, movimentando o jogador rapidamente em uma direção e o tornando invencível por um curto período de tempo.  
* __Mouse:__ Use o mouse para indicar ao jogador onde atirar.  
* __Botão Esquerdo do Mouse:__ Atira.

### Objetivo
O seu objetivo é acumular o máximo de pontos antes de esgotar seus pontos de vida.  
Você pode aumentar sua pontuação se mantendo vivo por mais tempo ou matando inimigos.

### Inimigos
* __Vespão:__ Persegue o jogador e atira em sua direção.  
*  __Aranha:__ Persegue o jogador rapidamente e atira em um padrão para 8 direções.  
* __Besouro:__ Persegue o jogador lentamente, atira em um padrão complicado e se defende após atirar.  
_Cuidado!_ Enquanto o Besouro se defende ele irá refletir seus tiros de volta caso seja atingido.  

## Diagrama UML de Classes
O diagrama UML de Classes do projeto foi criado com auxilio do py2puml, tendo sido modificado a partir do arquivo PlantUML gerado pela ferramenta de linha de comando.

No diagrama é possível observar os conceitos de programação orientada a objetos, como herança, interfaces, abstração, encapsulamento e polimorfismo.  
Também está representado como o código foi modularizado, ilustrando qual arquivo contem quais classes e como elas se relacionam.


![Diagrama UML de Classes](https://github.com/Brugger-UFMG/POO-Projeto_Final/blob/bc5d9668694c6752684075f8ae58f434af5a412b/docs/diagrama%20UML.png)
